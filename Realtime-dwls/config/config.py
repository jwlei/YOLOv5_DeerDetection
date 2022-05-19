import configparser
import os

def generate_config():
    """ A function to generate the pre-defined configuration file. config.ini """
    config_path = 'config.ini'

    if not os.path.exists(config_path):
        print('[CONFIG] Could not find a configuration file ... \n[CONFIG] Creating default configuration file')
        config_file = configparser.ConfigParser(allow_no_value=True)

        config_file.add_section('Automatic')
        config_file.set('Automatic', '; Default settings when choosing [Automatic setup]:')

        config_file.set('Automatic', '\n; Resize output image:')
        config_file.set('Automatic', '; If this option is set to False, the GUI will wrap the original resolution of the input source.')
        config_file.set('Automatic', '; Legal values: True, False')
        config_file.set('Automatic', 'resizeOutput', 'True')

        config_file.set('Automatic', '\n; Resolution in px to process video at:')
        config_file.set('Automatic', '; This option is only used if resizeOutput = True')
        config_file.set('Automatic', 'width', '640')
        config_file.set('Automatic', 'height', '480')

        config_file.set('Automatic', '\n; Launch directly with config values and skip all setup in the application:')
        config_file.set('Automatic', '; Legal values: True, False')
        config_file.set('Automatic', 'SkipSetup', 'False')

        config_file.set('Automatic', '\n; Start separate MQTT Subscriber client:')
        config_file.set('Automatic', '; Legal values: True, False')
        config_file.set('Automatic', 'startMQTTsubscriber', 'True')

        config_file.set('Automatic', '\n; Default video source to load when choosing [Automatic setup]:')
        config_file.set('Automatic', 'VideoSource', 'resources/media/demo_reel.mp4')

        config_file.set('Automatic', '\n; Default model to load when choosing [Automatic setup]:')
        config_file.set('Automatic', 'ModelSource', 'resources/models/defaultModel.pt')

        config_file.set('Automatic', '\n; If there is no present .pt model on the disc, fetch from remote URL:')
        config_file.set('Automatic', 'RemoteModelUrl', 'https://dl.dropboxusercontent.com/s/3y47tbcz6e33a40/yolov5M.pt')

        config_file.set('Automatic', '\n; Whether the application should save raw images on detection:')
        config_file.set('Automatic', '; Legal values: True, False')
        config_file.set('Automatic', 'captureDetection', 'False')

        config_file.set('Automatic', '\n; The frequency in seconds at which images are saved on detection ')
        config_file.set('Automatic', '; Legal values: 1, 2, ... 58, 59')
        config_file.set('Automatic', 'captureFrequency', '5')

        config_file.set('Automatic', '\n; If the application should reload the pyTorch cache on start-up:')
        config_file.set('Automatic', '; Legal values: True, False')
        config_file.set('Automatic', 'forceReload', 'True')

        config_file.set('Automatic', '\n; Set the confidence value for which prediction to mark as a detection:')
        config_file.set('Automatic', '; E.g. if the threshold is set to 0.7, predictions with a confidence value')
        config_file.set('Automatic', '; greater than 0.7 will trigger the detected status.')
        config_file.set('Automatic', '; Legal values: 0.0-1.0')
        config_file.set('Automatic', 'detectionThreshold', '0.6')

        config_file.set('Automatic', '\n; If the application run in headless mode, without GUI')
        config_file.set('Automatic', '; Legal values: True, False')
        config_file.set('Automatic', 'headless', 'False')

        with open(r"config.ini", 'w') as configfileObj:
            config_file.write(configfileObj)
            configfileObj.flush()
            configfileObj.close()
            print(f"[CONFIG] Default configuration file 'config.ini' created at {config_path}")

    else:
        print('[CONFIG] Configuration found.\n')
        print('[CONFIG] If you wish to generate a fresh default configuration:')
        print('[CONFIG] Delete your config.ini file.\n')

        
            

            

