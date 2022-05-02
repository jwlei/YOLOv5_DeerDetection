import queue
import subprocess
import os
import cv2
import configparser

from sys import executable, stderr
from subprocess import Popen, CREATE_NEW_CONSOLE

from gui.gui_output import Gui_output
from setup.startup_setup import Setup
from processing.process import Process

import config.config






class Main:
    """ The main application class which is ran when starting the application """ 

    def __init__(self, windowTitle, videoSource, modelSource, forceReload_flag, captureDetection, detectionThreshold, captureFrequency, output_dim, headless_mode, resize_flag):
        """
        Initialization of the main class

        :param str windowTitle: Title of the window which is set in the setup
        :param str videoSource: String representation of videoSource URL or Path
        :param str modelSource: String representation of modelSource URL or Path
        :param bool forceReload_flag: Boolean flag if the application should reload the PyTorch cache
        :param bool captureDetection: Boolean flag if images of detections should be saved
        :param float detectionThreshold: Decides confidence threshold at which is considered a detection
        :param int captureFrequency: Minimum interval in seconds between saving each picture
        :param output_dim:
        :param bool headless_mode: Boolean flag if application is running in headless mode
        :param bool resize_flag: Boolean flag if video output should be resized
        """

        # Initialization of references and default values
        self.callback_queue = queue.LifoQueue(maxsize = 1)  # Initialize a LastInn-FirstOut queue which will fetch and execute callbacks
                                                            # Maxsize = 1 to ensure that the freshest frame is always the one processed and shown by the GUI
        self.headless_mode = headless_mode                  # Boolean flag if the application should run in headless mode
        self.current_frame = None                           # Reference for current_frame
        self.newVideoSource = None                          # New video source reference
        self.sourceTitle = videoSource                      # Reference for the title of a source
        self.fps = self.getFps()                            # Get and set FPS for the video_source
        self.callbackUpdateDelay = 10                       # Initialize the delay in which the callback waits for re-execution
                                                            # math.floor(1000/self.fps)
        

        # Initialize the GUI by calling the Gui_video_output
        if not headless_mode:
            self.gui = Gui_output(self.on_exit, 
                                    self.sourceTitle,
                                    windowTitle,
                                    Process.getNewVideoSource, 
                                    Process.getNewModelSource)
            self.gui.root.protocol("WM_DELETE_WINDOW", self.on_exit)  # Callback for when GUI window get's closed.
        else:
            self.gui = None

        # Initialize a thread which fetches the Video input
        self.process_thread = Process(self.gui, 
                                      self.callback_queue,
                                      self.fps,
                                      videoSource, 
                                      modelSource, 
                                      forceReload_flag,
                                      captureDetection,
                                      captureFrequency,
                                      detectionThreshold,
                                      output_dim,
                                      headless_mode,
                                      resize_flag)

        # Start the processing thread and callback loop
        if not headless_mode:
            self.launch_process_thread()    # If we're in headless, we've already launched it
            self.callback_get_input()       # Start the callback loop, if we're in headless we don't need it 

    def launch_gui(self):
        """ Function to launch the GUI """
        self.gui.launch()


    def launch_process_thread(self):
        """ Function to start the process thread """ 
        self.process_thread.start()


    def callback_get_input(self):
        """ Callback function which listens for a new frame and executes """
        try:
            self.callback_get_input
                 
            callback = self.callback_queue.get_nowait() # Get the item from the que
            callback()
                    
        except queue.Empty:
            # If the que is empty, run the callback to get a frame
            self.gui.root.after(self.callbackUpdateDelay, self.callback_get_input)
        else:
            self.gui.root.after(self.callbackUpdateDelay, self.callback_get_input)


    def on_exit(self):
        """ Function for closing the process when closing the GUI """
        try:
            self.process_thread.stop()              # Stop the thread

            try:
                self.process_thread.join()          # Merge the threads
            except Exception:
                pass

            self.process_thread.release_resources() # Release the video resource
        
            if not self.headless_mode:
                self.gui.root.destroy()             # Destroy the GUI window

            if mqtt_subscriber_started:
                mqtt_subscriber.kill()              # Close the MQTT subprocess
            
        except Exception:
            pass

        
    def __del__(self):
        """ Finalizer to stop the thread """ 
        self.process_thread.stop()


    def getFps(self):
        """ Function to get FPS from video source to send down the pipeline
         Default to 30 fps if no data is available


         :returns: fps: FPS from input source or set by the system if not available
         """
        vid = cv2.VideoCapture(videoSource)
        fps = vid.get(cv2.CAP_PROP_FPS)

        if fps >= 1 and fps <= 60:
            print('[SETUP] FPS set to: ', fps)
            return fps
        else:
            fps = 30
            print('[SETUP] FPS could not be read from video source, set to default: ', fps)
            return fps


            
        

# ------------------------------------------ Launch configuration ------------------------------------------ #

checkConf = config.config
checkConf.generate_config()


# _____________________/ Load default configuration \_____________________ #
config_automatic = configparser.ConfigParser(allow_no_value=True)
config_automatic.read('config.ini')

skipSetup = config_automatic['Automatic'].getboolean('SkipSetup')
mqtt_subscriber_started = config_automatic['Automatic'].getboolean('startMQTTsubscriber')

defaultRemoteModelUrl = config_automatic['Automatic']['RemoteModelUrl']
defaultModelSource = config_automatic['Automatic']['ModelSource']


model_exists = os.path.exists(defaultModelSource)

if mqtt_subscriber_started:
    mqtt_subscriber = Popen([executable, 'external_mqtt/ext_MQTT_Subscriber.py'], subprocess.CREATE_NEW_CONSOLE)




# _____________________/ Launch with the config values \_____________________ #
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
        detectionThreshold = config_automatic['Automatic'].getfloat('detectionThreshold')
        captureFrequency = config_automatic['Automatic'].getint('captureFrequency')
        output_width = config_automatic['Automatic'].getint('width')
        output_height = config_automatic['Automatic'].getint('height')
        output_dim = output_width, output_height
        headless_mode = config_automatic['Automatic'].getboolean('headless')
        resize_flag = config_automatic['Automatic'].getboolean('resizeOutput')
        



if not skipSetup:
    # Start setup for launching the program
    pick = Setup.setManualOrAutomatic() 

    # _____________________/ Automatic setup  \_____________________ #
    if pick == 'Automatic':
        print('[SETUP] Automatic setup initiated')

        main = Main("DWLS [Automatic setup]", videoSource, modelSource, forceReload, captureDetection, detectionThreshold, captureFrequency, output_dim, headless_mode, resize_flag)

        print('[SETUP] Launching with:')
        print('[SETUP] SOURCE VIDEO: ', videoSource)
        print('[SETUP] SOURCE MODEL: ', modelSource)
        print('[SETUP] FORCE RELOAD: ', forceReload)
        print('[SETUP] SAVING DETECTIONS: ', captureDetection)
        if captureDetection:
            print(f'[SETUP] CAPTURE FREQUENCY {captureFrequency}s')
        print('[SETUP] DETECTION CONFIDENCE THRESHOLD: ', detectionThreshold)
        print('[SETUP] IMAGE WILL BE RESIZED: ', resize_flag)
        if resize_flag:
            print(f'[SETUP] OUTPUT RESOLUTION SET TO {output_width}x{output_height}px')
        print('[SETUP] HEADLESS MODE: ', headless_mode)
    
        if not headless_mode:
            main.launch_gui()
        else:
            main.launch_process_thread()


    # _____________________/ Manual setup \_____________________ #
    # The user defines the settings in the application
    elif pick == 'Manual':
        print('[SETUP] Manual setup initiated')

        # TODO: Write video source adress / model to source.txt file and use it in automatic or let them be available for picking when starting up next time
        videoSource = Setup.setVideoSource()
        modelSource = Setup.setModelSource()
        if modelSource == 'Default':
            modelSource = defaultModelSource
        forceReload = Setup.setForceReload()
        captureDetection = Setup.setCaptureDetection()
        if captureDetection:
            captureFrequency = Setup.setCaptureFrequency()
        detectionThreshold = Setup.setDetectionThreshold()
        resize_flag = Setup.setResize()
        if resize_flag:
            output_dim = Setup.setResolution()
        headless_mode = Setup.setHeadless()

        main = Main("DWLS Object [Manual setup]", videoSource, modelSource, forceReload, captureDetection, detectionThreshold, captureFrequency, output_dim, headless_mode, resize_flag)

        print('[SETUP] Launching with:')
        print('[SETUP] SOURCE VIDEO: ', videoSource)
        print('[SETUP] SOURCE MODEL: ', modelSource)
        print('[SETUP] FORCE RELOAD: ', forceReload)
        print('[SETUP] SAVING DETECTIONS: ', captureDetection)
        if captureDetection:
            print(f'[SETUP] CAPTURE FREQUENCY {captureFrequency}s')
        print('[SETUP] DETECTION CONFIDENCE THRESHOLD: ', detectionThreshold)
        print('[SETUP] IMAGE WILL BE RESIZED: ', resize_flag)
        if resize_flag:
            print(f'[SETUP] OUTPUT RESOLUTION SET TO {output_width}x{output_height}px')
        print('[SETUP] HEADLESS MODE: ', headless_mode)
    

        if not headless_mode:
            main.launch_gui()
        else:
            main.launch_process_thread()

    # _____________________/ Image gathering  \_____________________ #
    # Mode for gathering images for further training of model
    elif pick == 'Gather images':
        print('[SETUP] Image collection setup initiated')

        videoSource = Setup.setVideoSource()
        # Default model
        # Force reload false
        captureDetection = True
        captureFrequency = Setup.setCaptureFrequency()
        detectionThreshold = Setup.setDetectionThreshold() #detectionThreshold = '0.3' 
        headless_mode = Setup.setHeadless()

        print('[SETUP] Launching with:')
        print('[SETUP] SOURCE VIDEO: ', videoSource)
        print('[SETUP] SOURCE MODEL: ', modelSource)
        print('[SETUP] FORCE RELOAD: ', forceReload)
        print('[SETUP] SAVING DETECTIONS: ', captureDetection)
        print('[SETUP] DETECTION CONFIDENCE THRESHOLD: ', detectionThreshold)
        print('[SETUP] IMAGE WILL BE RESIZED: ', resize_flag)
        if resize_flag:
            print(f'[SETUP] OUTPUT RESOLUTION SET TO {output_width}x{output_height}px')
        print('[SETUP] HEADLESS MODE: ', headless_mode)


        main = Main("DWLS [Image Collection]", videoSource, modelSource, forceReload, captureDetection, detectionThreshold, captureFrequency, output_dim, headless_mode, resize_flag)

        if not headless_mode:
            main.launch_gui()
        else:
            main.launch_process_thread()

    # _____________________/ Setup is skipped \_____________________ #
    # Runs straight of the configuration file with no GUI prompts
elif skipSetup:
    main = Main("DWLS [Skipped setup, running on config]", videoSource, modelSource, forceReload, captureDetection, detectionThreshold, captureFrequency, output_dim, headless_mode, resize_flag)

    print('[SETUP] All setup skipped, running on settings found in config.ini')
    print('[SETUP] Launching with:')
    print('[SETUP] SOURCE VIDEO: ', videoSource)
    print('[SETUP] SOURCE MODEL: ', modelSource)
    print('[SETUP] FORCE RELOAD: ', forceReload)
    print('[SETUP] SAVING DETECTIONS: ', captureDetection)
    print('[SETUP] DETECTION CONFIDENCE THRESHOLD: ', detectionThreshold)
    print('[SETUP] IMAGE WILL BE RESIZED: ', resize_flag)
    if resize_flag:
        print(f'[SETUP] OUTPUT RESOLUTION SET TO {output_width}x{output_height}px')
    print('[SETUP] HEADLESS MODE: ', headless_mode)    

    if not headless_mode:
        main.launch_gui()
    else:
        main.launch_process_thread()


