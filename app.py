from multiprocessing import Process, Queue

# Import custom subpackages
from core import config, monitor, viewer
from common import utils, logger, recorder, database

import signal, sys, os
import threading, pkgutil
import time


## Initialize the logger
logger = logger.get_logger('voltazero_monitor')

## Define main thread stop flag
#StopFlag = threading.Event()


def signal_handler(signum, frame):
    """A signal handler which sets the stop flag if a termination signal is triggered

       :signum: the signal number
       :frame: the stack frame which triggered the signal
    """
    logger.info('Stop flag raised. Main thread is stopping...')
    #StopFlag.set()



if __name__ == '__main__':

    ## Clear console
    utils.clear_console()
    
    ## Setup stop signal handler
    #signal.signal(signal.SIGTERM, signal_handler)
    #signal.signal(signal.SIGINT, signal_handler)
    #signal.signal(signal.SIGABRT, signal_handler)
    #signal.signal(signal.SIGQUIT, signal_handler)
    print(f'Main: {os.getpid()}')

    ## Initialization
    config_file = "./core/config.json"

    ## Setup telemetry queue
    q = Queue()

    ## Read the application config
    appConfig = config.AppConfig(config_file)
    rc = appConfig.load_app_config()

    if rc == -1:
        logger.error(f'The configuration file cannot be found!')
        sys.exit()
    elif rc == -2:
        logger.error(f'An exception has occured. Application will stop!')
        sys.exit()
    else:
        logger.info(f'App configuration loaded and parsed successfully.')
    
    ## Establish connectivity to the MQTT broker
    pmonitor = monitor.Monitor(appConfig, q, client_id="cp100")
    pmonitor.start()

    ## Initialize and start database recorder
    trecorder = recorder.Recorder(q, appConfig)
    trecorder.start()

    ## Start viewer    
    viewer = viewer.Viewer(appConfig, window_title='Sensors data')
    viewer.start()

    ## Sleep main thread
    while True:
        try:
            time.sleep(500)
        except KeyboardInterrupt:
            print("Stopping all threads and processes...")
            break  
    
    try:

        ## Stop the monitor process
        pmonitor.stop()
        pmonitor.join()

        ## Stop the recorder thread
        trecorder.stop()
        trecorder.join()

        ## stop viewer
        viewer.stop()
        viewer.join()
    except Exception as e:
        print(f'Exception: {str(e)}')

    ## For debug, check the data remaining in the queue
    data = []

    while not q.empty():
        data.append(q.get())

    print(data)

    
    