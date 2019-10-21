
## Import custom subpackages
from core import config
from common import utils, database

## Import standard packages
from platform import system
from threading import Timer, Thread, Event, currentThread

import matplotlib
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
from matplotlib import style
from matplotlib.figure import Figure
from matplotlib.dates import DateFormatter, MinuteLocator

import matplotlib.pyplot as plt
import numpy as np
import datetime
import time
import logging


### Initialize logger for the module
logger = logging.getLogger('voltazero_monitor')

## Use WXAgg backend for matplot because Tkinter is not thread-safe
#matplotlib.use('WXAgg')

## Specify the plotting style
plt.style.use('ggplot')


def plt_maximize():
    
    """ This function maximizes the plot window.
        The original code has been taken from a StackOverflow post,
        but was altered to suite the purpose of this project.
        See: https://stackoverflow.com/a/54708671
    """

    backend = plt.get_backend()
    cfm = plt.get_current_fig_manager()

    if backend == "wxAgg":
        cfm.frame.Maximize(True)
    elif backend == "TkAgg":
        pos = str(system()).lower()
        if pos == "win32" or pos == 'windows':
            cfm.window.state('zoomed')              # This works on windows only
        else:
            cfm.resize(*cfm.window.maxsize())
    elif backend == 'QT4Agg':
        cfm.window.showMaximized()
    elif callable(getattr(cfm, "full_screen_toggle", None)):
        if not getattr(cfm, "flag_is_max", None):
            cfm.full_screen_toggle()
            cfm.flag_is_max = True
    else:
        raise RuntimeError("plt_maximize() is not implemented for current backend:", backend)



class Viewer(Thread):


    def __init__(self, appconfig, window_title='Sensors data'):
    
        """ Initializes the viewer object

        :param appconfig: the application configuration object        
        :param window_title: the plot window title
        """

        Thread.__init__(self)
        self.running = Event()
        self.id = currentThread().getName()
        self.appconfig = appconfig
        self.enabled = False 
        self.window_title = window_title

        self.sensors = ["T0 ($^\circ$C)", "T1 ($^\circ$C)", "Th ($^\circ$C)", "IR (V)", "LS (V)", "Buzz. State"]
        self.timestamps = []
        self.t0 = []
        self.t1 = []
        self.th = []
        self.ir = []
        self.bz = []
        self.ls = []
        self.columns = [self.timestamps, self.t0, self.t1, self.th, self.ir, self.ls, self.bz]


    def start(self):
    
        """Starts the viewer thread"""        

        self.running.set()
        self.enabled = True
        super(Viewer, self).start()


    def stop(self):
    
        """Stops the viewer thread"""  

        self.running.clear()  


    def run(self):
    
        """ Runs the viewer infinite loop """

        # Initialize plot
        self.init_viewer()

        try:
            # insert data in database
            while (self.running.isSet()):
                ## Update plot
                self.fetch_and_format_data()

                ## Set window title
                self.fig.canvas.set_window_title(f"{self.window_title} - Last update: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")  
                
                self.draw()

                ## Sleep viewer thread
                time.sleep(self.appconfig.viewer_interval)                

            ## Declare the thread instance disabled
            self.enabled = False

        except Exception as e:
            logger.error(f"An exception has occured [{str(e)}]")


    def draw(self):
    
        """Updates and plots the curves"""

        if (len(self.timestamps) > 0):
            min_x_lim = utils.get_datetime_with_offset(self.timestamps[0], -10)
            max_x_lim = utils.get_datetime_with_offset(self.timestamps[len(self.timestamps)-1], 10)

            for i in range(6):
                if len(self.axs[i].lines) > 0:
                    self.axs[i].lines.remove(self.axs[i].lines[0])

                self.axs[i].plot(self.columns[0], self.columns[i+1], color='royalblue')
                self.axs[i].set_xlim(min_x_lim, max_x_lim)
        
        plt.savefig(f'img/image_{datetime.datetime.timestamp(datetime.datetime.now())}.png')
        plt.show(block=False)
        plt.pause(0.0001)


    def init_viewer(self):

        """Initializes the plot window and figure"""

        # Turn on matplotlib interactive mode
        plt.ion()

        # Creates just a figure and only one subplot
        self.fig, self.axs = plt.subplots(6, sharex=True)
        
        try:
            # Maximize window
            plt_maximize()
        
            # Set up the subplots' properties
            for i in range(6):
                self.axs[i].set_ylabel(self.sensors[i])            
                self.axs[i].xaxis.set_major_locator(mdates.MinuteLocator())
                self.axs[i].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
                self.axs[i].xaxis.set_minor_locator(ticker.AutoMinorLocator())
                self.axs[i].xaxis.set_minor_formatter(ticker.NullFormatter())
                
                self.axs[i].xaxis_date()
                self.axs[i].autoscale_view()
                self.axs[i].grid(which='major', axis='both', alpha=.3)
               
        except Exception as e:
            print(f'Exception: {str(e)}')


    def fetch_and_format_data(self):

        """Fetches data from database and formats the retrieved data for plotting"""
        
        try:
            ## Retrieve data from database
            db_connect = database.connect(self.appconfig.database_filename)
            data = database.retrieve_data(db_connect, self.appconfig.time_window, self.appconfig.table_name)
            database.disconnect(db_connect) 

            logger.debug(f"Total retrieved records: {len(data)}")

            ## Format retrieved data
            self.timestamps = []
            self.t0 = []
            self.t1 = []
            self.th = []
            self.ir = []
            self.bz = []
            self.ls = []

            for item in data:
                self.timestamps.append(datetime.datetime.strptime(item.timestamp, '%Y/%m/%d %H:%M:%S'))
                self.t0.append(item.t0 if not (item.t0 == None) else np.nan)
                self.t1.append(item.t1 if not (item.t1 == None) else np.nan)
                self.th.append(item.th if not (item.th == None) else np.nan)
                self.ir.append(item.ir if not (item.ir == None) else np.nan)
                self.ls.append(item.ls if not (item.ls == None) else np.nan)
                self.bz.append(item.bz if not (item.bz == None) else np.nan)
                print(f"{item}")           

            self.columns = [self.timestamps, self.t0, self.t1, self.th, self.ir, self.ls, self.bz]
                  
            return 0

        except Exception as e:
            logger.error(f"An exception has occured [{str(e)}]")
            return -1
        