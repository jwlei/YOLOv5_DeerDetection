import queue
import subprocess
import os
import cv2

from typing import DefaultDict
from sys import executable
from subprocess import Popen, CREATE_NEW_CONSOLE

from app_controller.gui_output import Gui_output
from app_controller.process import Process
from app_view.startup_setup import Setup



class Main:
    """ The main application class which is ran """ 

    def __init__(self, title, videoSource, modelSource, forceReload, captureDetection, detectionThreshold):
        """ Initialization of the main class """ 
        self.sourceTitle = videoSource
        

        # Initialize a LastInn-FirstOut queue which will fetch and execute callbacks
        # Maxsize = 1 to ensure that the freshest frame is always the one processed and shown by the GUI
        self.callback_queue = queue.LifoQueue(maxsize = 1)
        

        # Initialization of default values
        # Reference for current_frame
        self.current_frame = None
        # Get and set FPS for the video_source
        self.fps = self.getFps()
        # New video source reference
        self.newVideoSource = None
        # Initialize the delay in which the callback waits for re-execution
        self.callbackUpdateDelay = 1
        
        # Initialize the GUI by calling the Gui_video_output
        self.gui = Gui_output(self.on_exit, Process.getNewVideoSource, Process.getNewModelSource, self.sourceTitle)
        # Initialize a thread which fetches the Video input
        self.process_thread = Process(self.gui, self.callback_queue, videoSource, modelSource, forceReload, self.fps, captureDetection, detectionThreshold)
        
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


            
        


# ------------------------------------------ Launch configuration ------------------------------------------ #
defaultModelUrl = 'https://dl.dropboxusercontent.com/s/f530z37pdale1v8/defaultModel.pt'
defaultModelSource = 'resources/models/defaultModel.pt'
model_exists = os.path.exists(defaultModelSource)
# Launch the program with the following parameters
if __name__ == "__main__":
        #videoSource = "https://www.youtube.com/watch?v=8SDm48ieYP8"
        videoSource = 'resources/media/video_testLong.mp4'
        if not model_exists:
            print('[SETUP]: Default model not present, fetching ...')
            modelSource = Setup.downloadModel(defaultModelUrl)
        else:
            modelSource = defaultModelSource
        forceReload = False
        captureDetection = False
        detectionThreshold = 0.5
        


# Create subprocess for MQTT subscriber client
mqtt_subscriber = Popen([executable, 'utility/MQTT_Subscriber.py'], subprocess.CREATE_NEW_CONSOLE)

# Start setup for launching the program
pick = Setup.setManualOrAutomatic() 

# If automatic, use defined values
if pick == 'Automatic':
    print('[SETUP] Automatic setup initiated')

    main = Main("Deer Detection [Automatic setup]", videoSource, modelSource, forceReload, captureDetection, detectionThreshold)

    print('[SETUP] Launching with:')
    print('[SETUP] SOURCE VIDEO: ', videoSource)
    print('[SETUP] SOURCE MODEL: ', modelSource)
    print('[SETUP] FORCE RELOAD: ', forceReload)
    print('[SETUP] SAVING DETECTIONS: ', captureDetection)
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

    main = Main("Deer Detection [Manual setup]", videoSource, modelSource, forceReload, captureDetection, detectionThreshold)

    print('[SETUP] Launching with:')
    print('[SETUP] SOURCE VIDEO: ', videoSource)
    print('[SETUP] SOURCE MODEL: ', modelSource)
    print('[SETUP] FORCE RELOAD: ', forceReload)
    print('[SETUP] SAVING DETECTIONS: ', captureDetection)
    print('[SETUP] DETECTION CONFIDENCE THRESHOLD: ', detectionThreshold)

    main.launch()

elif pick == 'Gather images':
    print('[SETUP] Image collection setup initiated')

    videoSource = Setup.setVideoSource()
    # Default model
    # Force reload false
    captureDetection = True
    detectionThreshold = '0.3'
    #detectionThreshold = StartupSetup.setDetectionThreshold()

    print('[SETUP] Launching with:')
    print('[SETUP] SOURCE VIDEO: ', videoSource)
    print('[SETUP] SOURCE MODEL: ', modelSource)
    print('[SETUP] FORCE RELOAD: ', forceReload)
    print('[SETUP] SAVING DETECTIONS: ', captureDetection)
    print('[SETUP] DETECTION CONFIDENCE THRESHOLD: ', detectionThreshold)

    main = Main("Deer Detection [Manual setup]", videoSource, modelSource, forceReload, captureDetection, detectionThreshold)

    main.launch()





    
    


