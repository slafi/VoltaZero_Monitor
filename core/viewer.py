from threading import Timer, Thread, Event, currentThread
#from common import logger, database

from matplotlib.figure import Figure
from platform import system

import matplotlib.pyplot as plt
import numpy as np
import datetime
import time
import logging

### Initialize logger for the module
logger = logging.getLogger('voltazero_monitor')


def plt_maximize():
    # See discussion: https://stackoverflow.com/questions/12439588/how-to-maximize-a-plt-show-window-using-python
    backend = plt.get_backend()
    cfm = plt.get_current_fig_manager()

    if backend == "wxAgg":
        cfm.frame.Maximize(True)
    elif backend == "TkAgg":
        pos = str(system()).lower()
        if pos == "win32" or pos == 'windows':
            cfm.window.state('zoomed')  # This is windows only
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


    def __init__(self):
        self.sensors = ["Temp. (t0)", "Light Sensor", "Buzz. State", "Temp. (t1)", "Thermo. (th)", "Infrared Sensor"]


    def init(self, window_title='Sensors data'):
        # Creates just a figure and only one subplot
        self.fig, self.axs = plt.subplots(6, sharex=True)

        # Some example data to display
        x = np.linspace(0, 2 * np.pi, 400)
        y = np.sin(x ** 2)

        for i in range(6):
            self.axs[i].plot(x, y)
            self.axs[i].grid(True)
            self.axs[i].set_ylabel(self.sensors[i])

        #set window title
        self.fig.canvas.set_window_title(f"{window_title} - Last update: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        try:
            # Maximize window
            plt_maximize()
        except Exception as e:
            print(f'Exception: {str(e)}')

        # Show plot
        plt.show()



if __name__ == "__main__":

    viewer = Viewer()
    viewer.init()