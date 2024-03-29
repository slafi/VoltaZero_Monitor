
from core import telemetry

from multiprocessing import Process, Queue
from datetime import datetime

import json
import paho.mqtt.client as mqtt
import os
import logging


# Initialize logger for the module
logger = logging.getLogger('voltazero_monitor')


class Monitor(Process):

    """ Initiates a new process to connect to the server and retrieve
        telemetry data using the MQTT protocol

        :param appconfig: the application configuration object
        :param q: the telemetry data queue
        :param client: the MQTT client
        :param client_id: the MQTT client identifier
        :param pid: the recorder process identifier
        :param stopped: a flag indicating if the process is running
        :param subscribed: a flag indicating if the client is subscribed to the topic
        :param connected: a flag indicating if the client is connected to the MQTT server
    """

    def __init__(self, appconfig, q, client_id):

        """ Initializes the monitor object

            :param q: the telemetry data queue
            :param appconfig: the application configuration object
            :param client_id: the assigned client identifier
        """

        super(Monitor, self).__init__()

        self.appconfig = appconfig
        self.q = q
        self.subscribed = False
        self.connected = False
        self.client_id = client_id
        self.stopped = True
        self.client = None


    def init_connection(self):

        """ Initializes the connection to the MQTT broker

            :return: 0 if success or -1 if an exception is raised
        """

        try:
            self.client = mqtt.Client(client_id=self.client_id,
                                      clean_session=True)
            self.client.username_pw_set(username=self.appconfig.username,
                                        password=self.appconfig.secret)
            self.client.on_connect = self.on_connect
            self.client.on_message = self.on_message
            self.client.on_subscribe = self.on_subscribe
            self.client.connect(self.appconfig.host, self.appconfig.port)

            return 0

        except Exception as e:
            logger.error(f"Exception: {str(e)}")
            return -1


    def run(self):

        """ Runs the monitor loop

            :return: 0 if success or -1 if an exception is raised
        """

        try:
            self.PID = os.getpid()
            logger.info(f'Monitor PID: {os.getpid()}')

            self.stopped = False
            self.init_connection()

            if self.client is not None:
                while not self.stopped:
                    self.client.loop()

            return 0

        except Exception as e:
            logger.error(f"Exception: {str(e)}")
            return -1


    def stop(self):

        """ Stops the monitor process

            :return: 0 if success or -1 if an exception is raised
        """

        try:
            self.stopped = True

            if self.client is not None and self.connected is True:
                self.client.unsubscribe(self.appconfig.topic)
                self.client.disconnect()
                self.connected = False
                self.subscribed = False

            super(Monitor, self).terminate()
            return 0

        except Exception as e:
            logger.error(f"Exception: {str(e)}")
            return -1


    def on_message(self, client, userdata, message):

        """ The on_message handler parses the MQTT message data and initializes
            the telemetry object

            :param client: the MQTT client
            :param userdata: the user data object
            :param message: the telemetry message
        """

        try:
            if self.q is None:
                self.q = Queue()

            # Decode and parse the telemetry data
            data = json.loads(message.payload.decode('ascii'))
            ts = datetime.now().strftime('%Y/%m/%d %H:%M:%S')

            t0, t1, th, bz, lg, ir, id = self.handle_telemetry(data)
            tlm = telemetry.Telemetry(timestamp=ts, t0=t0, t1=t1, th=th, bz=bz, ls=lg, ir=ir, id=id)

            self.q.put(tlm)

            logger.debug(f"{str(tlm)}")

        except Exception as e:
            logger.error(f"Exception: {str(e)}")


    def on_subscribe(self, client, userdata, mid, granted_qos):

        """ The on_subscribe handler attempts to subscribe to the given topic

            :param client: the MQTT client
            :param userdata: the user data object
            :param mid: the message identifier
            :param granted_qos: the granted QoS
        """

        self.subscribed = True


    def on_connect(self, client, userdata, flags, rc):

        """ The on_connect handler attempts to connect to the MQTT broker

            :param client: the MQTT client
            :param userdata: the user data object
            :param flags: a list of flags indicating the clean_session status
            :param rc: the returned code
        """

        if rc == 0:
            self.connected = True
            logger.info(self.parse_return_code(0))
            self.client.subscribe(self.appconfig.topic)
        else:
            logger.error(f"{self.parse_return_code(rc)}")
            self.connected = False


    def handle_telemetry(self, data):

        """ Parses the telemetry data and returns the sensors' readings
            and device identifier

            :param data: the MQTT message payload
            :return: t0, t1, th, bz, lg, ir, id: sensors' readings and
                     device identifier
        """

        try:
            if(data["id"] != 'null'):
                id = data["id"]
            else:
                id = 'NULL'

            if(data["t0"] != 'null'):
                t0 = float(data["t0"])
            else:
                t0 = 'NULL'

            if(data["t1"] != 'null'):
                t1 = float(data["t1"])
            else:
                t1 = 'NULL'

            if(data["th"] != 'null'):
                th = float(data["th"])
            else:
                th = 'NULL'

            if(data["ir"] != 'null'):
                ir = float(data["ir"])
            else:
                ir = 'NULL'

            if(data["lg"] != 'null'):
                lg = float(data["lg"])
            else:
                lg = 'NULL'

            if(data["bz"] != 'null'):
                bz = int(data["bz"])
            else:
                bz = 'NULL'

            return t0, t1, th, bz, lg, ir, id

        except Exception as e:
            logger.error(f"Exception: {str(e)}")
            return None


    def parse_return_code(self, rc):

        try:
            """ returns the appropriate connection status given the broker's return code
                got when connection is attempted

            :param rc: the MQTT broker return code
            :return: connection_status: the actual connection status
                     if success, None otherwise
            """
            # 0: Connection successful
            if rc == 0:
                return 'Connection established successfully'

            # 1: Connection refused – incorrect protocol version
            if rc == 1:
                return 'Connection refused – incorrect protocol version'

            # 2: Connection refused – invalid client identifier
            if rc == 2:
                return 'Connection refused – invalid client identifier'

            # 3: Connection refused – server unavailable
            if rc == 3:
                return 'Connection refused – server unavailable'

            # 4: Connection refused – bad username or password
            if rc == 4:
                return 'Connection refused – bad username or password'

            # 5: Connection refused – not authorised

            if rc == 5:
                return 'Connection refused – not authorised'

            # 6-255: Currently unused.
            if rc >= 6:
                return 'Unknown connection status'

        except Exception as e:
            logger.error(f"Exception: {str(e)}")
            return None
