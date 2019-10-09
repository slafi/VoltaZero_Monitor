from common import utils, logger

import os, sys, inspect
import logging

### Initialize logger for the module
logger = logging.getLogger('voltazero_monitor')



class Telemetry():


    def __init__(self, timestamp=None, t0=None, t1=None, th=None, bz=None, ls=None, ir=None, id=None):
        if timestamp == None:
            self.timestamp = utils.get_unix_timestamp()
        else:
            self.timestamp = timestamp
            
        self.t0 = t0
        self.t1 = t1
        self.th = th
        self.bz = bz
        self.ls = ls
        self.ir = ir
        self.id = id


    def __repr__(self):
        return f"{self.id} @ {self.timestamp} => (t0: {self.t0}, t1: {self.t1}, " \
               f"th: {self.th}, ls: {self.ls}, ir: {self.ir}, bz: {self.bz})"
    
