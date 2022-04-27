from os import startfile
import threading
import cv2
import math
import time
import paho.mqtt.client as mqtt
import geocoder
import json
import time

from PIL import Image, ImageTk

from app_controller.gui_output import Gui_output
from app_model.input_handler import Input_handler
from app_view.startup_setup import Setup


# Global variables
newVideoSource = None
newModelSource = None
noInput = False
times = []

class Process(threading.Thread):
    """ Class where thread is running to get a frame from the input data and call processing functions on the frame """


    def __init__(self, gui, callback_queue, fps, videoSource, modelSource, forceReload_flag, savingDetection_flag, captureFrequency, detectionThreshold, output_dim, headless_mode, resize_flag):
        """ Initialize the thread """

        # Call the super class constructor
        threading.Thread.__init__(self)

        # Initialize an MQTT publisher client
        self.mqttBroker = "mqtt.eclipseprojects.io"
        self.client = mqtt.Client("DEER_DETECTOR")
        self.client.connect(self.mqttBroker)
        print('[MQTT Publisher] Client started')

        # Initialize references to variables
        self.gui = gui
        self.callback_queue = callback_queue
        self.fps = int(700/math.floor(fps)) # Set delay a bit faster than frame time since we're processing the frames
                                            # Convert float FPS number to INT for cv2 waitkey
                                            # Floor vs roof, decided to use floor so we dont process more frames than we have
        self.videoSource = videoSource
        self.modelSource = modelSource
        self.forceReload = forceReload_flag
        self.captureDetection = savingDetection_flag
        self.captureFrequency = captureFrequency
        self.detectionThreshold = detectionThreshold
        self.output_dim = output_dim
        self.headless_mode = headless_mode
        self.resize_flag = resize_flag

        # Default values
        self.rawFrame = None
        self.waitingToStop = False # Flag for if the process should stop
        self.runningStatus = False # Flag for current status of thread
        ipLocation = geocoder.ip('me')
        self.currentLocation = str(ipLocation.latlng) # Location based on the current IP-Adress
        self.currentTime = None
        self.detected_flag = None
        self.detectedCount = 0

        self.jsonMessage = None
        

        print('[SETUP] FPS set to: ', fps)
        print(f'[SETUP] DELAY set to {self.fps}ms')

        # Create an instance of the input data
        self.input_handler = Input_handler(self.videoSource, 
                                            self.modelSource, 
                                            self.forceReload, 
                                            self.captureDetection,
                                            self.captureFrequency,
                                            self.detectionThreshold)

        if not self.headless_mode:
            # Set initial save detecion flag
            self.gui.update_savingDetection_status(savingDetection_flag)

    
    def run(self):
        """ The thread's run method """
        global newVideoSource
        global newModelSource
        global noInput
        
        while (True):
            # While the thread is running
            # Check if the thread should quit or not
            if (self.waitingToStop):
                self.runningStatus = True
                break
            
            # Checking if source is changed
            if newVideoSource is not None:
                self.videoSource = newVideoSource
                self.gui.update_title_from_input_source(self.videoSource)
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

            
            if(ret == False):
                # If the return value of the input_instance is false, display no_input
                noInput = True
                if not self.headless_mode:
                    self.gui.update_output_image(ImageTk.PhotoImage(Image.open('resources/media/image_no-input.jpg')))
                    self.gui.update_title_from_input_source('No input')
                    msg = 'NO INPUT FROM VIDEO SOURCE'
                    self.jsonMessage = json.dumps({'msg' : msg,
                                       'time' : self.currentTime, 
                                       'location' : self.currentLocation,  
                                       'detected' : self.detected_flag, 
                                       'detectedCount' : self.detectedCount,   
                                       }, indent = 4)
                    
            else:
                noInput = False
            

            if not noInput and not self.headless_mode:
            # If the callback_queue is not full, put the current frame into the queue for execution of the thread
                if self.callback_queue.full() == False:
                    self.callback_queue.put((lambda: self.score_label_send_to_output(self.current_frame, self.rawFrame, self.gui)))

                # If the callback_queue is full, remove the item in the queue and put the current frame into the queue for execution of the thread
                elif self.callback_queue.full() == True:
                    self.callback_queue.get()
                    self.callback_queue.put((lambda: self.score_label_send_to_output(self.current_frame, self.rawFrame, self.gui)))

            # If running in headless mode, skip the callback and directly score and label the frame
            elif not noInput and self.headless_mode:                                     
                self.score_label_send_to_output(self.current_frame,
                                                self.rawFrame,
                                                self.gui)


            # Publish the JSON list through MQTT
            self.client.publish("DEER_DETECTION", self.jsonMessage)
            
            # Wait for delay until next iteration
            cv2.waitKey(self.fps) 

    
    def score_label_send_to_output(self, current_frame, rawFrame, gui):
        """ 
        Function where the current frame is processed
        This function is used as callback and executed by the thread 
        """
        global detected_flag
        global detectedCount
        global currentTime

        # For each iteration, reset values
        detected_flag = None
        detectedCount = 0
        currentTime = None
        
        start_time = time.time() # Start time for measuring performance

        if self.resize_flag:
            current_frame = self.input_handler.resize_frame(current_frame, self.output_dim)
        
        # Score the frame and get the labels and coordinates from the current frame
        labels, cord = self.input_handler.predict_with_model(current_frame)
        prediction = labels, cord

        # Plot bounding box and label to the frame
        frame, detected_flag, detectedCount = self.input_handler.plot_frame(prediction, current_frame, rawFrame)

        # Process the frame for output and update the GUI
        if not self.headless_mode:
            
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)                          # Convert the frame to RGB  
            output_image = Image.fromarray(frame)                                   # Convert the image from array to PIL in order to show it using tkinter
            output_image = ImageTk.PhotoImage(output_image)                         # Convert the image to a Tkinter compatible Image 

            gui.update_output_image(output_image)                                   # Update the output image with the current image
            gui.update_alarm_status(detected_flag)                                  # Update the current alarm status


        
        # JSON MQTT Message                                                                           
        currTimePreFormat = time.localtime()                                        # Location is gotten in the initialization
        self.currentTime = time.strftime('%Y-%m-%d %H:%M:%S', currTimePreFormat)    # Current Time
        self.set_detected(detected_flag)                                            # Set detection status for MQTT
        self.set_detectedCount(detectedCount)                                       # Set counter for how many animals detected

        # Creating a json message to send with MQTT
        self.jsonMessage = json.dumps({'time' : self.currentTime, 
                                       'location' : self.currentLocation,  
                                       'detected' : self.detected_flag, 
                                       'detectedCount' : self.detectedCount,
                                       }, indent = 4)

        

        executionTime = (time.time() - start_time)*1000                             # End time for measuring performance
        self.calculateAverageProcessingTime(executionTime)                          # Calculate average frametime and print to console

        
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
        self.detected_flag = detection

    def set_detectedCount(self, detectedCount):
        """ Function to set detectedCount """ 
        self.detectedCount = detectedCount

    def get_detection(self):
        """ Function to get detected """ 
        return self.detected_flag

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
        self.gui.update_title_from_input_source(newVideoSource)

    def calculateAverageProcessingTime(self, executionTime):
        """ Function to measure execution time per frame, for optimization and testing purposes """
        global times

        times.append(executionTime)

        if len(times) >= 1000:
            sum_num = 0
            for t in times:
                sum_num = sum_num + t           

            avg = sum_num / len(times)
            print(f'----------- AVERAGE EXECUTION TIME PER FRAME MEASURED OVER {len(times)} FRAMES -----------')
            print(f'{avg}ms')
            times = []