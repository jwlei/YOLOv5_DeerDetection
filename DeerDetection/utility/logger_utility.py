import logging



def singleton(cls):
    instances = {}

    def get_instance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return get_instance()

@singleton
class Logger:
    """ Class to handle logging in application """ 
    def __init__(self):
        
        file_log_main = "docs/log_application.txt"

        # Logging basic config for MQTT 
        logging.basicConfig(filename = file_log_main, # Log to fresh file
                        filemode = 'w',           # every launch
                        level=logging.DEBUG,
                        encoding = 'utf-8', 
                        format = '%(asctime) %(levelname)s: %(modulename)s - %(message)s')

        self.loggr = logging.getLogger('root')

        logging.warning('[DeerDetector Logger] Initializing')
        logging.warning(f'[DeerDetector Logger] Main application log can be found at {file_log_main}')

        # Just getting a fresh file to write detections in
        # TODO: New log file on each run (?)
        write_to_log = open(file_log_main, "w") # "a" if we rather want to append
        write_to_log.write('')
        write_to_log.close()

