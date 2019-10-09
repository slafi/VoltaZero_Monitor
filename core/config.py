import json
import os.path, os, sys, inspect
import logging

### Initialize logger for the module
logger = logging.getLogger('voltazero_monitor')


class AppConfig():


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
        self.batch_size = None


    def load_app_config(self):

        """ Attempts to load the application configuration object

        :return: return code if success, -1 if the file does not exist and
        -2 if an exception arises
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
            logger.error('Exception: {}'.format(e))
            return -2
            

    def parse_app_config(self, data):

        """ Attempts to parse the configuration file

        :return: 0 if success, -1 if an exception arises
        """

        try:

            self.host = data["host"]
            self.port = data["port"]
            self.username = data["username"]
            self.secret = data["secret"]
            self.mac_address = data["mac_address"]
            self.topic = data["topic"]
            self.database_filename = data["database"]
            self.table_name = data["table_name"]
            self.time_window = data["time_window"]
            self.batch_size = data["batch_size"]
            
            return 0

        except Exception as e:
            logger.error('Exception: {}'.format(e))
            return -1