import queue
import subprocess
import os
import cv2
import math
import configparser


from sys import executable
from subprocess import Popen, CREATE_NEW_CONSOLE

from app_controller.gui_output import Gui_output
from app_view.startup_setup import Setup
from app_controller.process import Process
import utility.config






class Main:
    """ The main application class which is ran when starting the application """ 

    def __init__(self, title, videoSource, modelSource, forceReload, captureDetection, detectionThreshold, captureFrequency):
        """ Initialization of the main class """ 
        self.sourceTitle = videoSource
        

        # Initialize a LastInn-FirstOut queue which will fetch and execute callbacks
        # Maxsize = 1 to ensure that the freshest frame is always the one processed and shown by the GUI
        self.callback_queue = queue.LifoQueue(maxsize = 1)
        

        # Initialization of default values
        # Reference for current_frame
        self.current_frame = None
        # New video source reference
        self.newVideoSource = None

        # Get and set FPS for the video_source
        self.fps = self.getFps()
        # Initialize the delay in which the callback waits for re-execution
        self.callbackUpdateDelay = 10 # math.floor(1000/self.fps)
        
        # Initialize the GUI by calling the Gui_video_output
        self.gui = Gui_output(self.on_exit, 
                              self.sourceTitle,
                              title,
                              Process.getNewVideoSource, 
                              Process.getNewModelSource)

        # Initialize a thread which fetches the Video input
        self.process_thread = Process(self.gui, 
                                      self.callback_queue, 
                                      videoSource, 
                                      modelSource, 
                                      forceReload, 
                                      self.fps, 
                                      captureDetection,
                                      captureFrequency,
                                      detectionThreshold)
        
        # Callback for when GUI window get's closed.
        self.gui.root.protocol("WM_DELETE_WINDOW", self.on_exit)

        # Start the input source by calling the process thread
        self.start_input_source()  
        # Start the callback loop
        self.callback_get_input()    

    def launch(self):
        """ Function to launch the GUI """
        self.gui.launch()


    def start_input_source(self):
        """ Function to start the thread """ 
        self.process_thread.start()


    def callback_get_input(self):
            """ Callback function which listens for a new frame and executes """
            # Try to get a callback from the process thread
            try:
                self.callback_get_input
                
                # Empty the que
                callback = self.callback_queue.get_nowait()
                callback()
                    
            except queue.Empty:
                # If the que is empty, run the callback to get a frame
                self.gui.root.after(self.callbackUpdateDelay, self.callback_get_input)
            else: 
                self.gui.root.after(self.callbackUpdateDelay, self.callback_get_input)


    def on_exit(self):
        """ Function for closing the process when closing the GUI """
        try:
            # Stop the thread
            self.process_thread.stop()

            # Merge the threads
            try:
                self.process_thread.join()
            except Exception:
                pass

            # Release the video resource
            self.process_thread.release_resources()
        
            # Destroy the GUI window
            self.gui.root.destroy()

            # Close subprocess
            if startMQTTsubscriber:
                mqtt_subscriber.kill()
            
        except Exception:
            pass

        
    def __del__(self):
        """ Finalizer to stop the thread """ 
        self.process_thread.stop()

    def getFps(self):
        """ Function to get FPS from video source to send down the pipeline """ 
        vid = cv2.VideoCapture(videoSource)
        fps = vid.get(cv2.CAP_PROP_FPS)

        if fps >= 1:
            print('[SETUP] FPS set to: ', fps)
            return fps
        else:
            # Default to 30 fps if no data is available
            fps = 30
            print('[SETUP] FPS could not be read from video source, set to default: ', fps)
            return fps


            
        

# TODO: Replace with config file stuff
# ------------------------------------------ Launch configuration ------------------------------------------ #

# Create subprocess for MQTT subscriber client and config
#config_exec = Popen([executable, 'utility/config.py'], subprocess.CREATE_NEW_CONSOLE)

checkConf = utility.config
checkConf.generate_config()



config_automatic = configparser.ConfigParser(allow_no_value=True)
config_automatic.read('config.ini')

# Load default config




skipSetup = config_automatic['Automatic'].getboolean('SkipSetup')
startMQTTsubscriber = config_automatic['Automatic'].getboolean('startMQTTsubscriber')

defaultRemoteModelUrl = config_automatic['Automatic']['RemoteModelUrl']
defaultModelSource = config_automatic['Automatic']['ModelSource']

model_exists = os.path.exists(defaultModelSource)
if startMQTTsubscriber:
    mqtt_subscriber = Popen([executable, 'utility/MQTT_Subscriber.py'], subprocess.CREATE_NEW_CONSOLE)

# Launch the program with the following parameters
if __name__ == "__main__":
        videoSource = config_automatic['Automatic']['VideoSource']
        if not model_exists:
            print('[SETUP]: Default model not present, fetching default from the cloud ... ')
            print(f'[SETUP: Fetching from URL: {defaultRemoteModelUrl}]')
            modelSource = Setup.downloadModel(defaultRemoteModelUrl)
        else:
            modelSource = defaultModelSource
        forceReload = config_automatic['Automatic'].getboolean('forceReload')
        captureDetection = config_automatic['Automatic'].getboolean('captureDetection')
        detectionThreshold = config_automatic['Automatic'].getint('captureFrequency')
        captureFrequency = config_automatic['Automatic'].getfloat('detectionThreshold')
        

if not skipSetup:
    # Start setup for launching the program
    pick = Setup.setManualOrAutomatic() 

    # If automatic, use defined values
    if pick == 'Automatic':
        print('[SETUP] Automatic setup initiated')

        main = Main("Deer Detection [Automatic setup]", videoSource, modelSource, forceReload, captureDetection, detectionThreshold, captureFrequency)

        print('[SETUP] Launching with:')
        print('[SETUP] SOURCE VIDEO: ', videoSource)
        print('[SETUP] SOURCE MODEL: ', modelSource)
        print('[SETUP] FORCE RELOAD: ', forceReload)
        print('[SETUP] SAVING DETECTIONS: ', captureDetection)
        if captureDetection:
            print(f'[SETUP] CAPTURE FREQUENCY {captureFrequency}s')
        print('[SETUP] DETECTION CONFIDENCE THRESHOLD: ', detectionThreshold)
    
        main.launch()

    # If manual, use values defined by the user
    elif pick == 'Manual':
        print('[SETUP] Manual setup initiated')

        # TODO: Write video source adress / model to source.txt file and use it in automatic or let them be available for picking when starting up next time
        videoSource = Setup.setVideoSource()
        modelSource = Setup.setModelSource()
        if modelSource == 'Default':
            modelSource = defaultModelSource
        forceReload = Setup.setForceReload()
        captureDetection = Setup.setCaptureDetection()
        detectionThreshold = Setup.setDetectionThreshold()
        captureFrequency = Setup.setCaptureFrequency()

        main = Main("Deer Detection [Manual setup]", videoSource, modelSource, forceReload, captureDetection, detectionThreshold, captureFrequency)

        print('[SETUP] Launching with:')
        print('[SETUP] SOURCE VIDEO: ', videoSource)
        print('[SETUP] SOURCE MODEL: ', modelSource)
        print('[SETUP] FORCE RELOAD: ', forceReload)
        print('[SETUP] SAVING DETECTIONS: ', captureDetection)
        if captureDetection:
            print(f'[SETUP] CAPTURE FREQUENCY {captureFrequency}s')
        print('[SETUP] DETECTION CONFIDENCE THRESHOLD: ', detectionThreshold)
    

        main.launch()

    # Mode for gathering images for further training of model
    # TODO: User defined interval on pictures saved
    elif pick == 'Gather images':
        print('[SETUP] Image collection setup initiated')

        videoSource = Setup.setVideoSource()
        # Default model
        # Force reload false
        captureDetection = True
        captureFrequency = Setup.setCaptureFrequency()
        detectionThreshold = Setup.setDetectionThreshold() #detectionThreshold = '0.3'

        print('[SETUP] Launching with:')
        print('[SETUP] SOURCE VIDEO: ', videoSource)
        print('[SETUP] SOURCE MODEL: ', modelSource)
        print('[SETUP] FORCE RELOAD: ', forceReload)
        print('[SETUP] SAVING DETECTIONS: ', captureDetection)
        print('[SETUP] DETECTION CONFIDENCE THRESHOLD: ', detectionThreshold)

        main = Main("Deer Detection [Image Collection]", videoSource, modelSource, forceReload, captureDetection, detectionThreshold, captureFrequency)

        main.launch()

elif skipSetup:
    main = Main("Deer Detection [Skipped setup, running on config]", videoSource, modelSource, forceReload, captureDetection, detectionThreshold, captureFrequency)

    main.launch()






    
    


