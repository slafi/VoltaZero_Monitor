from multiprocessing import Queue

# Import custom subpackages
from core import config, monitor, viewer
from common import utils, logger, recorder

import os
import sys
import time


# Initialize the logger
logger = logger.get_logger('voltazero_monitor')


if __name__ == '__main__':

    # Clear console
    utils.clear_console()

    logger.info(f'--------------------------------------------------')
    logger.info(f'Main PID: {os.getpid()}')

    # Initialization
    config_file = "./core/config.json"

    # Setup telemetry queue used by the Monitor and Recorder
    q = Queue()

    # Read the application config
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

    # Start the Monitor and establish connection to the MQTT broker
    pmonitor = monitor.Monitor(appConfig, q, client_id="cp100")
    pmonitor.start()

    # Initialize and start database recorder
    trecorder = recorder.Recorder(q, appConfig)
    trecorder.start()

    # Start viewer if required
    if(not appConfig.no_viewer):
        viewer = viewer.Viewer(appConfig, window_title='Sensors data')
        viewer.start()
    else:
        logger.info('The viewer is disabled.')

    try:
        # Sleep main thread
        while True:
            time.sleep(1)

    except Exception as e:
        print(f'Exception: {str(e)}')

    except KeyboardInterrupt:
        logger.info("Stopping all threads and processes... (This may take few seconds)")

        # Stop the monitor process
        pmonitor.stop()
        pmonitor.join()

        # Stop the recorder thread
        trecorder.stop()
        trecorder.join()

        # Stop viewer process if already started
        if(not appConfig.no_viewer):
            viewer.stop()
            viewer.join()
