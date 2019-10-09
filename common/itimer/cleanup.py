


class AllJobsTerminated(Exception):
    
    """This class is a special exception that is raised if a job assigned to
       a thread should be properly terminated
    """

    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


def signal_cleanup_handler(signum, frame):

    """A function that cleans up the thread job properly if a specific signal is emitted.

       :raises:
           AllJobsTerminated: a job termination exception.
    """

    raise AllJobsTerminated