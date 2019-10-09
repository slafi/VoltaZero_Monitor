from os import system, name
from datetime import datetime

from common import logger

import sys

import logging

### Initialize logger for the module
logger = logging.getLogger('voltazero_monitor')


def clear_console():

    """This function clears the console"""

    # for windows
    if name == 'nt': 
        _ = system('cls')
    # for mac and linux(here, os.name is 'posix') 
    else: 
        _ = system('clear')


def write_to_file(output_file, mode, text=''):
    """ Writes a text string to a file """
    try:
        ## Open output text file
        fid = open(output_file,mode)

        fid.write(text)

        fid.close()    
        
    except Exception as inst:
        logger.error("Exception: {}".format(inst))
        sys.exit()


def get_unix_timestamp():

    """Returns the UNIX timestamp from the current time and date"""
    # current date and time
    now = datetime.now()
    return datetime.timestamp(now)

