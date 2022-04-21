import threading
import input
import cv2
import numpy
import math
import torch

import time
import paho.mqtt.client as mqtt
import geocoder
import json


from PIL import Image, ImageTk
from time import time as tm
from gui_video_output import Gui_video_output
from input import Input


class ProcessThread(threading.Thread):
    """ Class where thread is running to get a frame from the input data and call processing functions on the frame """
    def __init__(self, gui, callback_queue, videoSource, modelSource, forceReload, fps, captureDetection, detectionThreshold):
        """ Initialize the thread """

        # Call the super class constructor
        threading.Thread.__init__(self)

        # Initialize an MQTT publisher client
        self.mqttBroker = "mqtt.eclipseprojects.io"
        self.client = mqtt.Client("DEER_DETECTOR")
        self.client.connect(self.mqttBroker)
        print('[MQTT Publisher] Client started')
        
        # Create an instance of the input data
        self.input_instance = Input(videoSource, modelSource, forceReload, captureDetection, detectionThreshold)

        # Convert float FPS number to INT for cv2 waitkey
        # Floor vs roof, decided to use floor so we dont process more frames than we have
        self.fps = math.floor(fps)
        print('[THREAD] FPS set to: ', self.fps)
       

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

        # While the thread is running
        while (True):

            # Check if the thread should quit or not
            if (self.waitingToStop):
                self.runningStatus = True
                break
            
            # Get a frame and return value from the input_instance
            ret, self.current_frame, self.rawFrame = self.input_instance.read_current_frame()
            
            
            # If the return value of the input_instance is false, print an error and exit the program
            if(ret == False):
                print('No input data')
                exit(-1)
            
            # If the callback_queue is not full, put the current frame into the queue for execution of the thread
            if self.callback_queue.full() == False:
                self.callback_queue.put((lambda: self.score_label_send_to_output(self.current_frame, self.rawFrame, self.gui)))

            # If the callback_queue is full, remove the item in the queue and put the current frame into the queue for execution of the thread
            elif self.callback_queue.full() == True:
                self.callback_queue.get()
                self.callback_queue.put((lambda: self.score_label_send_to_output(self.current_frame, self.rawFrame, self.gui)))

            # Send json list through MQTT
            self.client.publish("DEER_DETECTION", self.jsonMessage)


            
            # TODO: Match source video fps
            # Wait for delay until next iteration
            # Decides playback speed
  
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

        # Assign a start time to calculate and output FPS(frames per second) on the screen
        #start_time = tm()
        
        # Score the frame and get the labels and coordinates from the current frame
        labels, cord = self.input_instance.predict_with_model(current_frame)
        prediction = labels, cord

        # Plot graphics for the current frame
        frame, detected, detectedCount = self.input_instance.plot_frame(prediction, current_frame, rawFrame)

        # Assign end time to calculate and output FPS(frames per second) on the screen
        #end_time = tm()

        # Calculate the frames per second
        #onScreenFps = 1/numpy.round(end_time - start_time, 3)

        # Plot the frames per second unto the image
        #cv2.putText(frame, f'FPS: {int(onScreenFps)}', (20,70), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,255,0), 2)

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


        # Location is gotten in the initialization
     
        # Current Time
        currTimePreFormat = time.localtime()
        self.currentTime = time.strftime('%Y-%m-%d %H:%M:%S', currTimePreFormat)

        # Set detection status for MQTT
        self.set_detected(detected)
        
            

        # Set counter for how many animals detected
        self.set_detectedCount(detectedCount)

        # Creating a json message to send with MQTT
        self.jsonMessage = json.dumps({'time' : self.currentTime, 'location' : self.currentLocation,  'detected' : self.detected, 'detectedCount' : self.detectedCount}, indent = 4)


        
    def __del__(self):
        """ Finalizer to stop the process """
        self.input_instance.release()
            
    def release_resources(self):
        """ Function to release the resources """
        self.input_instance.release()
        
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

