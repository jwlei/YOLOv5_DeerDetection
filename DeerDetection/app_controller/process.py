import threading
import cv2
import numpy
import math
import time
import torch
import paho.mqtt.client as mqtt
import geocoder
import json


from PIL import Image, ImageTk
from time import time as tm

from app_controller.gui_output import Gui_output
from app_model.input_handler import Input_handler
from app_view.startup_setup import Setup

newVideoSource = None
newModelSource = None
noInput = False

class Process(threading.Thread):
    """ Class where thread is running to get a frame from the input data and call processing functions on the frame """
    def __init__(self, gui, callback_queue, fps, videoSource, modelSource, forceReload, captureDetection, captureFrequency, detectionThreshold):
        """ Initialize the thread """

        # Call the super class constructor
        threading.Thread.__init__(self)

        # Initialize an MQTT publisher client
        self.mqttBroker = "mqtt.eclipseprojects.io"
        self.client = mqtt.Client("DEER_DETECTOR")
        self.client.connect(self.mqttBroker)
        print('[MQTT Publisher] Client started')

        
        
        # Create an instance of the input data
        self.videoSource = videoSource
        self.modelSource = modelSource
        self.forceReload = forceReload
        self.captureDetection = captureDetection
        self.captureFrequency = captureFrequency
        self.detectionThreshold = detectionThreshold

        self.input_handler = Input_handler(self.videoSource, 
                                            self.modelSource, 
                                            self.forceReload, 
                                            self.captureDetection,
                                            self.captureFrequency,
                                            self.detectionThreshold)

        # Convert float FPS number to INT for cv2 waitkey
        # Floor vs roof, decided to use floor so we dont process more frames than we have
        self.fps = int(700/math.floor(fps)) # Set delay a bit faster than frame time since we're processing the frames
        print('[SETUP] FPS set to: ', fps)
        print(f'[SETUP] DELAY set to {self.fps}ms')
       

        # Initialize a reference for the callback queue
        self.callback_queue = callback_queue

        # Reference for RAW frame
        self.rawFrame = None
        
        # Initialize a reference for the GUI
        self.gui = gui
        self.gui.update_savingDetection_status(captureDetection)

        # Setup default values
        self.waitingToStop = False # Flag for if the process should stop
        self.runningStatus = False # Flag for current status of thread
   
        ipLocation = geocoder.ip('me')
        self.currentLocation = str(ipLocation.latlng)
        self.currentTime = None
        self.detected = None
        self.detectedCount = 0

        self.jsonMessage = None
    
        
       
    
    def run(self):
        """ The thread's run method """
        global newVideoSource
        global newModelSource
        global noInput
        # While the thread is running
        while (True):

            # Check if the thread should quit or not
            if (self.waitingToStop):
                self.runningStatus = True
                break
            
            # Checking if source is changed
            if newVideoSource is not None:
                self.videoSource = newVideoSource
                self.gui.update_title(self.videoSource)
                self.input_handler = Input_handler(self.videoSource, 
                                                    self.modelSource, 
                                                    self.forceReload, 
                                                    self.captureDetection,
                                                    self.captureFrequency,
                                                    self.detectionThreshold)
                print('[INFO] New video source selected: ', self.videoSource)
                newVideoSource = None

            if newModelSource is not None:
                self.modelSource = newModelSource
                self.input_handler = Input_handler(self.videoSource, 
                                                    self.modelSource, 
                                                    self.forceReload,
                                                    self.captureDetection,
                                                    self.captureFrequency,
                                                    self.detectionThreshold)
                print('[INFO] New model source selected: ', self.modelSource)
                newModelSource = None
               
            # Get a frame and return value from the input_instance
            ret, self.current_frame, self.rawFrame = self.input_handler.read_current_frame()
            
            
            # If the return value of the input_instance is false, display no_input
            if(ret == False):
                noInput = True
                self.gui.update_output_image(ImageTk.PhotoImage(Image.open('resources/media/image_no-input.jpg')))
                self.gui.update_title('No input')
            else:
                noInput = False
            
            if not noInput:
            # If the callback_queue is not full, put the current frame into the queue for execution of the thread
                if self.callback_queue.full() == False:
                    self.callback_queue.put((lambda: self.score_label_send_to_output(self.current_frame, 
                                                                                     self.rawFrame, 
                                                                                     self.gui)))

                # If the callback_queue is full, remove the item in the queue and put the current frame into the queue for execution of the thread
                elif self.callback_queue.full() == True:
                    self.callback_queue.get()
                    self.callback_queue.put((lambda: self.score_label_send_to_output(self.current_frame, 
                                                                                     self.rawFrame, 
                                                                                     self.gui)))

            # Publish the JSON list through MQTT
            self.client.publish("DEER_DETECTION", self.jsonMessage)

            # Wait for delay until next iteration
            cv2.waitKey(self.fps) 

    
    def score_label_send_to_output(self, current_frame, rawFrame, gui):
        """ 
        Function where the current frame is processed
        This function is used as callback and executed by the thread 
        """

        global detected
        global detectedCount
        global currentTime

        # For each iteration, set detection to False
        detected = None
        detectedCount = 0
        currentTime = None
        
        # Score the frame and get the labels and coordinates from the current frame
        labels, cord = self.input_handler.predict_with_model(current_frame)
        prediction = labels, cord

        # Plot bounding box and label to the frame
        frame, detected, detectedCount = self.input_handler.plot_frame(prediction, current_frame, rawFrame)


        # Convert the frame to RGB
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Resize the frame to dimensions width, height
        frame = cv2.resize(frame, (640, 480))

        # Convert the image from array to PIL in order to show it using tkinter
        image = Image.fromarray(frame)
        
        # Convert the image to a Tkinter compatible Image 
        image = ImageTk.PhotoImage(image)


        # Update the output image with the current image
        gui.update_output_image(image)
        # Update the current alarm status
        gui.update_alarm_status(detected)


        # JSON MQTT Message
        # Location is gotten in the initialization
        currTimePreFormat = time.localtime()
        self.currentTime = time.strftime('%Y-%m-%d %H:%M:%S', currTimePreFormat) # Current Time
        self.set_detected(detected) # Set detection status for MQTT
        self.set_detectedCount(detectedCount) # Set counter for how many animals detected

        # Creating a json message to send with MQTT
        self.jsonMessage = json.dumps({'time' : self.currentTime, 
                                       'location' : self.currentLocation,  
                                       'detected' : self.detected, 
                                       'detectedCount' : self.detectedCount}, 
                                      indent = 4)

        
    def __del__(self):
        """ Finalizer to stop the process """
        self.input_handler.release()
            
    def release_resources(self):
        """ Function to release the resources """
        self.input_handler.release()
        
    def stop(self):
        """ Function to set the stop Flag """
        self.waitingToStop = True

    def set_detected(self, detection):
        """ Function to set detected """
        self.detected = detection

    def set_detectedCount(self, detectedCount):
        """ Function to set detectedCount """ 
        self.detectedCount = detectedCount

    def get_detection(self):
        """ Function to get detected """ 
        return self.detected

    def getNewVideoSource():
        """ Function to get a new video source while running """ 
        global newVideoSource
        newVideoSource = Setup.setVideoSource()

    def getNewModelSource():
        """ Function to get a new model source while running """
        global newModelSource
        newModelSource = Setup.setModelSource()

    def getNewTitle(self):
        """ Function to get a new title from the video source while running """
        global newVideoSource
        self.gui.update_title(newVideoSource)