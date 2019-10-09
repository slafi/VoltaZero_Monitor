
from core import telemetry
from common import logger

from multiprocessing import Process, Queue
from datetime import datetime

import threading
import json
import paho.mqtt.client as mqtt
import os
import logging


### Initialize logger for the module
logger = logging.getLogger('voltazero_monitor')



class Monitor(Process):
    
    """ Initiates a new process to connect to the server and retrieve telemetry data
        using the MQTT protocol

        :param connection_handler: database connection handler
        :param appconfig: the application configuration object
        :param q: the telemetry data queue
        :param interval: the time interval at which telemetry data is stored
        :param batch_size: the maximum number of telemetry records stored at once
        :param id: the recorder thread identifier
        :param running: an event controlling the thread operation        
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
        self.Stopped = True


    def init_connection(self):
        try:
            self.client = mqtt.Client(client_id=self.client_id, clean_session=True)
            self.client.username_pw_set(username=self.appconfig.username, password=self.appconfig.secret)
            self.client.on_connect = self.on_connect
            self.client.on_message = self.on_message
            self.client.on_subscribe = self.on_subscribe
            self.client.connect(self.appconfig.host, self.appconfig.port)
            
            return 0
        except Exception as e:
            logger.error(f"Exception: {str(e)}")
            return -1


    def run(self):
        try:
            self.PID = os.getpid()
            #print(f"My PID: {self.PID}")
            self.Stopped = False
            self.init_connection()
            
            if self.client != None:
                while not self.Stopped:
                    self.client.loop()

            print(f"Process ID 2: {os.getpid()}")
            return 0
        except Exception as e:
            logger.error(f"Exception: {str(e)}")
            return -1
     

    def stop(self):
        try:
            self.Stopped = True

            if self.client != None and self.connected == True:
                self.client.unsubscribe(self.appconfig.topic)
                self.client.disconnect()
                self.connected = False
                self.subscribed = False
    
            return 0
        except Exception as e:
            logger.error(f"Exception: {str(e)}")
            return -1


    def on_message(self, client, userdata, message):
        try:
            if self.q == None:
                self.q =Queue()
            
            data = json.loads(message.payload.decode('ascii'))
            ts = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
            
            t0, t1, th, bz, lg, ir, id = self.handle_telemetry(data)
            tlm = telemetry.Telemetry(timestamp=ts, t0=t0, t1=t1, th=th, bz=bz, ls=lg, ir=ir, id=id)

            self.q.put(tlm)

            print(f'{str(tlm)}')

        except Exception as e:
            logger.error(f"Exception: {str(e)}")


    def on_subscribe(self, client, userdata, mid, granted_qos):
        self.subscribed = True


    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            print("connected OK")
            self.client.subscribe(self.appconfig.topic)
        else:
            print("Bad connection Returned code=", rc)
            self.connected = False


    def handle_telemetry(self, data):
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

    