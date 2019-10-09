
import threading, time, signal
import os
from datetime import timedelta



class InfiniteTimer(threading.Thread):

    """This class implements an infinitely-repeating timer in a seperate thread
    """

    def __init__(self, interval, job_funct, *args, **kwargs):

        """Custom class constructor

           :param interval: The time interval required to repeat the job function
           :param job_funct: The job function that should be exectued repeatedly
        """

        threading.Thread.__init__(self)
        self.daemon = False
        self.stopped = threading.Event()
        self.interval = timedelta(interval)
        self.job_funct = job_funct
        self.pid = os.getpid()
        self.args = args
        self.kwargs = kwargs
    

    def stop(self):

        """This function stops the infinite timer
        """

        self.stopped.set()
        self.join()
    

    def run(self):
        """This function runs the infinite timer loop
        """
        while not self.stopped.wait(self.interval.total_seconds()):
            self.job_funct(*self.args, **self.kwargs)


