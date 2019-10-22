import json
import os
import logging


# Initialize logger for the module
logger = logging.getLogger('voltazero_monitor')


class AppConfig():

    """ This class holdes the application configuration parameters

        :param config_filename: configuration filename
        :param host: the MQTT server domain name or IP address
        :param port: the MQTT server port
        :param username: the username used to connect to the MQTT server
        :param secret: the password used to connect to the MQTT server
        :param mac_address: the Helium device MAC address (might be used in
                            connection string)
        :param topic: MQTT topic
        :param database_filename: the SQlite database filename
        :param table_name: the data table name
        :param time_window: the time interval for telemetry display
        :param recorder_batch_size: the maximum number of telemetry records
                                    saved at once (used by the Recorder)
        :param recorder_interval: the recorder time interval
        :param viewer_interval: the viewer plot update interval
                                (used by the Viewer)
        :param no_viewer: if a flag indicating whether the viewer should start
    """

    def __init__(self, config_filename):

        """ Initializes the application configuration object

            :param config_filename: configuration filename (and path)
        """

        self.config_filename = config_filename
        self.host = None
        self.port = None
        self.username = None
        self.secret = None
        self.mac_address = None
        self.topic = None
        self.database_filename = None
        self.table_name = None
        self.time_window = None
        self.recorder_batch_size = None
        self.recorder_interval = None
        self.viewer_interval = None
        self.no_viewer = None


    def load_app_config(self):

        """ Attempts to load the application configuration object

            :return: return code if success, -1 if the file does not exist
                     and -2 if an exception arises
        """

        try:

            if not os.path.exists(self.config_filename):
                return -1
            else:
                with open(self.config_filename, 'r') as json_file:
                    data = json.load(json_file)
                    rcode = self.parse_app_config(data)
                    return rcode

        except Exception as e:
            logger.error(f'Exception: {str(e)}')
            return -2


    def parse_app_config(self, data):

        """ Attempts to parse the configuration file

            :return: 0 if success, -1 if an exception arises
        """

        try:

            # MQTT parameters
            self.host = data["host"]
            self.port = data["port"]
            self.username = data["username"]
            self.secret = data["secret"]
            self.mac_address = data["mac_address"]
            self.topic = data["topic"]

            # Database parameters
            self.database_filename = data["database"]
            self.table_name = data["table_name"]

            # Recorder parameters
            self.recorder_batch_size = data["recorder_batch_size"]
            self.recorder_interval = data["recorder_interval"]

            # Viewer parameters
            self.viewer_interval = data["viewer_interval"]
            self.time_window = data["time_window"]
            self.no_viewer = data["no_viewer"]

            return 0

        except Exception as e:
            logger.error(f'Exception: {str(e)}')
            return -1
