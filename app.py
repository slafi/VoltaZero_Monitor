from multiprocessing import Process, Queue

import os
import sys
import threading
import time

# Import custom subpackages
from core import config, monitor
from common import utils, logger, recorder, database


import pkgutil
import os.path

if __name__ == '__main__':

    ## Clear console
    utils.clear_console()
    
    ## Initialize the logger
    logger = logger.get_logger('voltazero_monitor')

    dirpath = os.getcwd()
    #print(f"Current directory is: {dirpath}")
    #print(f"Main ID: {os.getpid()}")

    ## Initialization
    config_file = "./core/config.json"

    ## Setup telemetry queue
    q = Queue()

    ## Read app config
    appConfig = config.AppConfig(config_file)
    rc = appConfig.load_app_config()

    if rc == -1:
        print(f'The configuration file cannot be found!')
        sys.exit()
    elif rc == -2:
        print(f'An exception has occured. Application will stop!')
        sys.exit()
    
    ## Establish connectivity to the MQTT broker
    pmonitor = monitor.Monitor(appConfig, q, client_id="cp100")
    pmonitor.start()

    ## Initialize and start database recorder
    precorder = recorder.Recorder(q, appConfig, interval=60.0, batch_size=20)
    precorder.start()

    time.sleep(60)

    ## Stop the monitor process
    pmonitor.terminate()
    pmonitor.join()

    ## Stop the recorder thread
    precorder.stop()
    precorder.join()

    ## Load data from the queue
    data = []

    while not q.empty():
        data.append(q.get())

    print(data)

    ## Launch telemetry viewer
    #p = Process(target=f, args=('bob',))
    #p.start()
    #p.join()