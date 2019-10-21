
from sqlite3 import Error
from datetime import datetime

from common import utils, logger
from core import telemetry

import sqlite3
import os, sys, inspect
import logging


### Initialize logger for the module
logger = logging.getLogger('voltazero_monitor')


# Initializes the database connection
def check_connection(db_filename, db_path=""):
    """ Checks if it is possible to establish a connection to the database

        :param db_filename: database filename
        :param db_path: the path to the database file
        :return: True if success or False if failure or an exception arises
    """
    try:
        if db_filename != None:
            db_name = os.path.join(db_path, db_filename)
            connection_handler = connect(db_name)
            if connection_handler != None:
                return True
            else:
                return False
        else:
            return False

    except sqlite3.Error as e:
        logger.error('Database connection error: {0}'.format(e))    
        return False
    finally:
        if connection_handler:
            connection_handler.close()


# Open a new connection handler to the database
def connect(db_filename, db_path=""):
    """ Creates a database connection handler to the SQLite database
        specified by the db_filename

        :param db_filename: database filename
        :param db_path: the path to the database file
        :return: Connection object or None
    """
    try:
        db_name = os.path.join(db_path, db_filename)
        connection_handler = sqlite3.connect(db_name)
        connection_handler.text_factory = sqlite3.OptimizedUnicode
        #print(sqlite3.version)

        return connection_handler
    except sqlite3.Error as e:
        logger.error('Database connection error: {0}'.format(e))    
        return None
    """finally:
        if connection_handler:
            connection_handler.close()"""


def create_datatable(connection_handler, table_name="data"):
    """
    Creates a new SQLite database and datatable where the telemetry will be stored
    :param connection_handler: the Connection object
    :param table_name: the data table name
    :return: 0 if succes, -1 if the connection handler is None and -2 if exception arises
    """
    try:
        sql = f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    t0_value FLOAT DEFAULT NULL,
                    t1_value FLOAT DEFAULT NULL,
                    th_value FLOAT DEFAULT NULL,
                    ir_value FLOAT DEFAULT NULL,
                    ls_value FLOAT DEFAULT NULL,
                    bz_value INTEGER DEFAULT NULL,
                    timestamp DATETIME,
                    db_timestamp DATETIME DEFAULT (DATETIME(CURRENT_TIMESTAMP))
                );
               """

        if connection_handler == None:
            return -1
            
        connection_handler.cursor().execute(sql)
        return 0

    except Exception as e:
        logger.error(f"Exception: {str(e)}")
        return -2


def insert_telemetry_data(connection_handler, data, table_name="data"):
    """
    Query the database to insert a list of telemetry records in the database
    :param connection_handler: the Connection object
    :param data: the list of telemetry records
    :param table_name: the data table name
    :return: count of inserted records or -1 if exception arises
    """
    try:
        cursor = connection_handler.cursor()

        sqlite_insert_query = f"""INSERT INTO `{table_name}`
                                ('t0_value', 't1_value', 'th_value', 'ir_value', 'ls_value', 'bz_value', 'timestamp') 
                                VALUES """

        # condition_if_true if condition else condition_if_false
        for i in range(len(data)):
            item = data[i]

            insert = f"({item[0]}, {item[1]}, {item[2]}, {item[3]}, {item[4]}, {item[5]}, '{item[6]}')"
            sqlite_insert_query = f"{sqlite_insert_query}{insert}"

            if i == len(data)-1:
                sqlite_insert_query = f"{sqlite_insert_query};"
            else:
                sqlite_insert_query = f"{sqlite_insert_query},"       

        count = cursor.execute(sqlite_insert_query)
        connection_handler.commit()
        cursor.close()

        logger.debug(f"Inserted rows: {cursor.rowcount}")
        return count

    except sqlite3.Error as error:
        logger.error(f"Exception: {str(error)}")
        return -1


def retrieve_data(connection_handler, time_window, table_name):
    """
    Query the database to get all telemetry records in a specified time window starting now
    :param connection_handler: the Connection object
    :param time_window: the time interval for the records lookup
    :param table_name: the data table name
    :return: list of telemetry records or None if exception arises
    """
    try:
        timestamp = datetime.fromtimestamp(utils.get_unix_timestamp() - time_window).strftime("%Y/%m/%d %H:%M:%S")
        cursor = connection_handler.cursor()
        cursor.execute(f"SELECT * FROM {table_name} WHERE timestamp >= ? ORDER BY timestamp ASC", (timestamp,))
    
        rows = cursor.fetchall()
    
        data = []
        for row in rows:
            tlm = telemetry.Telemetry(timestamp=row[7], t0=row[1], t1=row[2], th=row[3], bz=row[6], ls=row[5], ir=row[4], id=f"item_{row[0]}")
            data.append(tlm)

        cursor.close()
        return data

    except sqlite3.Error as error:
        logger.error(f"Exception: {str(error)}")
        return None


def check_if_datatable_exists(connection_handler, table_name="data"):
    """
    Query the database to check if the data table already eaxists
    :param connection_handler: the Connection object
    :param table_name: the data table name
    :return: True if exists and False if does not exist or exception arises
    """
    try:

        ### Check the list of tables
        cursor = connection_handler.cursor()
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table';")
        list_of_tables = cursor.fetchall()

        cursor.close()

        for item in list_of_tables:
            if table_name == item[0]:
                return True
            else :
                return False

    except sqlite3.Error as error:
        logger.error(f"Exception: {str(error)}")
        return False


# Closes the ongoing database connection if still alive
def disconnect(connection_handler):
    """
    Closes a current database connection
    :param connection_handler: the Connection object
    :return: 0 if success and -1 if an exception arises
    """
    try:
        if connection_handler != None:
            connection_handler.close()
        return 0
    except sqlite3.Error as e:
        logger.error('Database disconnection error: {0}'.format(e))
        return -1

        