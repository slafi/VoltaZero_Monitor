from threading import Timer, Thread, Event, currentThread
from common import logger, database

import datetime
import time
import logging


### Initialize logger for the module
logger = logging.getLogger('voltazero_monitor')


class Recorder(Thread):
    
    """ Initiates a connection to the database to store telemetry data
        at regular time intervals

        :param running: an event controlling the process operation
        :param appconfig: the application configuration object
        :param q: the telemetry data queue
        :param interval: the time interval at which telemetry data is retrieved
        :param batch_size: the maximum number of telemetry records stored at once
        :param id: the recorder thread identifier
        :param enabled: a flag indicating if the monitor is enabled        
    """

    def __init__(self, q, appconfig):

        """ Initializes the recorder object

        :param q: the telemetry data queue
        :param appconfig: the application configuration object        
        :param interval: the time interval at which telemetry data is stored
        :param batch_size: the maximum number of telemetry records stored at once
        """

        Thread.__init__(self)
        self.running = Event()
        self.id = currentThread().getName()
        self.q = q
        self.appconfig = appconfig
        self.enabled = False  


    def init_connection(self):

        """Initializes the database connection"""

        try:
            ## Attempt to connect to database (create database if does not already exist)
            self.connection_handler = database.connect(db_filename=self.appconfig.database_filename)

            ## If no connection handler, then give up
            if self.connection_handler == None:
                return -1
            else:
                # Create the datatable if it does not already exist
                if not database.check_if_datatable_exists(connection_handler=self.connection_handler, table_name=self.appconfig.table_name):
                    database.create_datatable(connection_handler=self.connection_handler, table_name=self.appconfig.table_name)
            
            return 0

        except Exception as error:
            logger.error(f"Exception: {str(error)}")
            return -2


    def start(self):

        """Starts the recorder thread"""
        
        self.running.set()
        self.enabled = True
        super(Recorder, self).start()
        
        
    def run(self):

        """ Runs the recorder infinite loop """

        # Opens database connection
        rcode = self.init_connection()
        
        if rcode == 0:
            # insert data in database
            while (self.running.isSet()):
                self.insert_batch(self.appconfig.recorder_batch_size)                
                time.sleep(self.appconfig.recorder_interval)                

            ## Store the remaning telemetry records in queue before closing connection
            if(self.enabled and not self.q.empty()):
                self.insert_batch(1000)

            # close data connection
            database.disconnect(self.connection_handler)
            self.enabled = False
        else:
            logger.error("Failed to initialize database connection")


    def insert_batch(self, size):

        """ Checks if it is possible to establish a connection to the database

        :param size: maximum number of items to save in the database in one time
        :return: list of telemetry records to insert in the database if success or None if failure or an exception arises
        """

        try:
            i = 0
            data = []
            while(i < size and not self.q.empty()):
                tlm = self.q.get()            
                arr = (tlm.t0, tlm.t1, tlm.th, tlm.ir, tlm.ls, tlm.bz, tlm.timestamp)
                data.append(arr)             
                i = i + 1

            if data != []:
                database.insert_telemetry_data(self.connection_handler, data, table_name=self.appconfig.table_name)
            
            logger.debug(f'Current queue size: {self.q.qsize()}')
            return data

        except Exception as inst:
            logger.error(f'Type: {type(inst)} -- Args: {inst.args} -- Instance: {inst}')
            return []


    def stop(self):

        """Stops the recorder thread"""  

        self.running.clear()       
