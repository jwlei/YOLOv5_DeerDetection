import configparser
import os

def generate_config():

    config_path = 'config.ini'

    if not os.path.exists(config_path):
        print('[CONFIG] Could not find a configuration file ... \n[CONFIG] Creating default configuration file')
        config_file = configparser.ConfigParser(allow_no_value=True)

        config_file.add_section('Automatic')
        config_file.set('Automatic', '; Default settings when choosing [Automatic setup]:')

        config_file.set('Automatic', '\n; Launch directly with config values and skip all prompts:')
        config_file.set('Automatic', '; Legal values: True, False')
        config_file.set('Automatic', 'SkipSetup', 'False')

        config_file.set('Automatic', '\n; Start separate MQTT Subscriber client:')
        config_file.set('Automatic', '; Legal values: True, False')
        config_file.set('Automatic', 'startMQTTsubscriber', 'True')

        config_file.set('Automatic', '\n; Default video source to load when choosing [Automatic setup]:')
        config_file.set('Automatic', 'VideoSource', 'https://www.youtube.com/watch?v=fpWVAZRb0R0')

        config_file.set('Automatic', '\n; Default model to load when choosing [Automatic setup]:')
        config_file.set('Automatic', 'ModelSource', 'resources/models/defaultModel.pt')

        config_file.set('Automatic', '\n; If there is no present .pt model on the disc, fetch from remote URL:')
        config_file.set('Automatic', 'RemoteModelUrl', 'https://dl.dropboxusercontent.com/s/f530z37pdale1v8/defaultModel.pt')

        config_file.set('Automatic', '\n; Whether the application should save raw images on detection:')
        config_file.set('Automatic', '; Legal values: True, False')
        config_file.set('Automatic', 'captureDetection', 'False')

        config_file.set('Automatic', '\n; The frequency in seconds at which images are saved on detection ')
        config_file.set('Automatic', '; Legal values: 1, 2, ... 58, 59')
        config_file.set('Automatic', 'captureFrequency', '5')

        config_file.set('Automatic', '\n; If the application should reload the pyTorch cache on start-up:')
        config_file.set('Automatic', '; Legal values: True, False')
        config_file.set('Automatic', 'forceReload', 'False')

        config_file.set('Automatic', '\n; Set the confidence value for which prediction to mark as a detection:')
        config_file.set('Automatic', '; E.g. if the threshold is set to 0.7, predictions with a confidence value')
        config_file.set('Automatic', '; greater than 0.7 will trigger the detected status.')
        config_file.set('Automatic', '; Legal values: 0.0-1.0')
        config_file.set('Automatic', 'detectionThreshold', '0.7')

        #config_file.add_section('Save directory for images:')
        #config_file.set('Save directory for images', 'saveDir', 'path/to')
   

        with open(r"config.ini", 'w') as configfileObj:
            config_file.write(configfileObj)
            configfileObj.flush()
            configfileObj.close()
            print(f"[CONFIG] Default configuration file 'config.ini' created at {config_path}")

    else:
        print('[CONFIG] Configuration found.\n')
        print('[CONFIG] If you wish to generate a fresh default configuration')
        print('[CONFIG] please delete your config.ini file.\n')

        
            

            

