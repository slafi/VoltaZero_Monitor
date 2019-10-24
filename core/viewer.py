
# Import custom subpackages
from common import utils, database

# Import standard packages
from platform import system
from threading import Thread, Event, currentThread

import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
import numpy as np
import datetime
import time
import logging


# Initialize logger for the module
logger = logging.getLogger('voltazero_monitor')

# Uncomment if you want to use WXAgg backend for matplotlib
# because Tkinter is inherently not thread-safe
# import matplotlib
# matplotlib.use('WXAgg')

# Specify the plotting style
plt.style.use('ggplot')


def plt_maximize():

    """ This function maximizes the plot window.
        The original code has been taken from a StackOverflow post,
        but was altered to suite the purpose of this project.
        See: https://stackoverflow.com/a/54708671
    """

    backend = plt.get_backend().lower()
    cfm = plt.get_current_fig_manager()

    if backend == "wxagg":
        cfm.frame.Maximize(True)
    elif backend == "tkagg":
        pos = str(system()).lower()
        if pos == "win32" or pos == 'windows':
            cfm.window.state('zoomed')        # This works on windows only
        else:
            cfm.resize(*cfm.window.maxsize())
    elif backend == 'qt4agg':
        cfm.window.showMaximized()
    elif callable(getattr(cfm, "full_screen_toggle", None)):
        if not getattr(cfm, "flag_is_max", None):
            cfm.full_screen_toggle()
            cfm.flag_is_max = True
    else:
        raise RuntimeError("plt_maximize() is not implemented for current backend:", backend)


class Viewer(Thread):

    """This class runs the telemetry plot viewer

       :param window_title: the plot window title
       :param appconfig: the application configuration object
       :param sensor_info: a list of sensor subplots properties
       :param columns: the list of telemetry data arrays
       :param enabled: a flag indicating if the viewer is enabled
       :param id: the viewer thread identifier
       :param running: an event controlling the thread operation
    """

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

        self.sensor_info = [
                            {
                                "title": 'T0 ($^\circ$C)',
                                "min_y_lim": 0,
                                "max_y_lim": 30,
                                "enable_y_limits": False
                            },
                            {
                                "title": "T1 ($^\circ$C)",
                                "min_y_lim": 0,
                                "max_y_lim": 100,
                                "enable_y_limits": True
                            },
                            {
                                "title": "Th ($^\circ$C)",
                                "min_y_lim": 0,
                                "max_y_lim": 100,
                                "enable_y_limits": True
                            },
                            {
                                "title": "IR (V)",
                                "min_y_lim": -0.1,
                                "max_y_lim": 5.1,
                                "enable_y_limits": True
                            },
                            {
                                "title": "LS (V)",
                                "min_y_lim": -0.1,
                                "max_y_lim": 5.1,
                                "enable_y_limits": True
                            },
                            {
                                "title": "Buzz. State",
                                "min_y_lim": -0.1,
                                "max_y_lim": 1.1,
                                "enable_y_limits": True
                            }
                        ]
        self.columns = [[], [], [], [], [], [], []]


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
                # Update plot
                nrecords = self.fetch_and_format_data()

                # Set window title
                self.fig.canvas.set_window_title(f"""{self.window_title} - [Last update: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Retrieved datapoints: {nrecords}]""")

                if (nrecords > 0):
                    self.draw()

                # Sleep viewer thread
                time.sleep(self.appconfig.viewer_interval)

            # Declare the thread instance disabled
            self.enabled = False

        except Exception as e:
            logger.error(f"Exception: {str(e)}")


    def draw(self):

        """Updates and plots the curves"""

        if (len(self.columns[0]) > 0):
            min_x_lim = utils.get_datetime_with_offset(self.columns[0][0], -10)
            max_x_lim = utils.get_datetime_with_offset(self.columns[0][len(self.columns[0])-1], 10)

            for i in range(6):
                if len(self.axs[i].lines) > 0:
                    self.axs[i].lines.remove(self.axs[i].lines[0])

                self.axs[i].plot(self.columns[0], self.columns[i+1],
                                 color='royalblue',
                                 marker="o")
                self.axs[i].set_xlim(min_x_lim, max_x_lim)

                # Uncomment if plot update's screenshot is required
                # plt.savefig(f'img/new/image_{datetime.datetime.timestamp(datetime.datetime.now())}.png')

                # Show plot without blocking the running process
                plt.show(block=False)
                plt.pause(0.0001)
        else:
            logger.info('No data to plot!')

            """for i in range(6):
                if len(self.axs[i].lines) > 0:
                    self.axs[i].lines.remove(self.axs[i].lines[0])

                self.axs[i].plot([], [], color='royalblue', marker="o")"""


    def init_viewer(self):

        """Initializes the plot window and figure"""

        # Turn on matplotlib interactive mode if necessary
        # plt.ion()

        # Creates just a figure and only one subplot
        self.fig, self.axs = plt.subplots(6, sharex=True)

        try:
            # Maximize window
            plt_maximize()

            # Set up the subplots' properties
            for i in range(6):
                info = self.sensor_info[i]
                self.axs[i].set_ylabel(info["title"])

                if(info["enable_y_limits"]):
                    self.axs[i].set_ylim(info["min_y_lim"], info["max_y_lim"])

                self.axs[i].xaxis.set_major_locator(plt.MaxNLocator(20))

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

        """Fetches data from database and formats the retrieved data for plotting

           :return : the number of retrieved data records, -1 if exception raises
        """

        try:
            # Retrieve data from database
            db_connect = database.connect(self.appconfig.database_filename)
            data = database.retrieve_data(db_connect, self.appconfig.time_window, self.appconfig.table_name)
            database.disconnect(db_connect)

            logger.debug(f"Total retrieved records: {len(data)}")

            # Format retrieved data
            timestamps = []
            t0 = []
            t1 = []
            th = []
            ir = []
            bz = []
            ls = []

            for item in data:
                timestamps.append(datetime.datetime.strptime(item.timestamp, '%Y/%m/%d %H:%M:%S'))
                t0.append(item.t0 if not (item.t0 is None) else np.nan)
                t1.append(item.t1 if not (item.t1 is None) else np.nan)
                th.append(item.th if not (item.th is None) else np.nan)
                ir.append(item.ir if not (item.ir is None) else np.nan)
                ls.append(item.ls if not (item.ls is None) else np.nan)
                bz.append(item.bz if not (item.bz is None) else np.nan)         

            self.columns = [timestamps, t0, t1, th, ir, ls, bz]

            return len(data)

        except Exception as e:
            logger.error(f"Exception: {str(e)}")
            return -1
