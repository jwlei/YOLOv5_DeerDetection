import threading
import input
import cv2
import numpy
import torch
from time import time
import paho.mqtt.client as mqtt

from PIL import Image, ImageTk

from gui_video_output import Gui_video_output
from input import Input


class ProcessThread(threading.Thread):
    """ Class where thread is running to get a frame from the input data and call processing functions on the frame """
    def __init__(self, gui, callback_queue, url):
        """ Initialize the thread """

        # Call the super class constructor
        threading.Thread.__init__(self)

        self.mqttBroker = "mqtt.eclipseprojects.io"
        self.client = mqtt.Client("DEER_DETECTOR")
        self.client.connect(self.mqttBroker)
        print('[MQTT Publisher] Client started')
        

        # Initialize a reference for the callback queue
        self.callback_queue = callback_queue

        # Initialize a reference for the url
        self.url = url
        
        # Initialize a reference for the GUI
        self.gui = gui

        # Setup default values
        self.detection = None
        self.waitingToStop = False # Flag for if the process should stop
        self.runningStatus = False # Flag for current status of thread
    
        # Create an instance of the input data
        self.input_instance = Input(url)
       
    
    def run(self):
        """ The thread's run method """

        # While the thread is running
        while (True):

            # Check if the thread should quit or not
            if (self.waitingToStop):
                self.runningStatus = True
                break
            
            # Get a frame and return value from the input_instance
            ret, self.current_frame = self.input_instance.read_current_frame()
            
            # If the return value of the input_instance is false, print an error and exit the program
            if(ret == False):
                print('No input data')
                exit(-1)
            
            # If the callback_queue is not full, put the current frame into the queue for execution of the thread
            if self.callback_queue.full() == False:
                self.callback_queue.put((lambda: self.score_label_send_to_output(self.current_frame, self.gui)))

            # If the callback_queue is full, remove the item in the queue and put the current frame into the queue for execution of the thread
            elif self.callback_queue.full() == True:
                self.callback_queue.get()
                self.callback_queue.put((lambda: self.score_label_send_to_output(self.current_frame, self.gui)))

            self.client.publish("DEER_DETECTION_LOG", self.detection)
            
            
            # TODO: Match source video fps
            # Wait for delay until next iteration
            # Decides playback speed
  
            cv2.waitKey(33) 

    
    def score_label_send_to_output(self, current_frame, gui):
        """ 
        Function where the current frame is processed
        This function is used as callback and executed by thread 
        """

        global detection
        # For each iteration, set detection to False
        detection = None

        # Assign a start time to calculate and output FPS(frames per second) on the screen
        start_time = time()

        # Score the frame and get the labels and coordinates from the current frame
        labels, cord = self.input_instance.predict_with_model(current_frame)
        prediction = labels, cord

        # Plot graphics for the current frame
        frame, detection = self.input_instance.plot_frame(prediction, current_frame)

        # Assign end time to calculate and output FPS(frames per second) on the screen
        end_time = time()

        # Calculate the frames per second
        fps = 1/numpy.round(end_time - start_time, 10)

        # Plot the frames per second unto the image
        cv2.putText(frame, f'FPS: {int(fps)}', (20,70), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,255,0), 2)

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
        gui.update_alarm_status(detection)

        # Set detection status for MQTT
        self.set_detection(detection)

        
    def __del__(self):
        """ Finalizer to stop the process """
        self.input_instance.release()

            
    def release_resources(self):
        """ Function to release the resources """
        self.input_instance.release()

        
    def stop(self):
        """ Function to set the stop Flag """
        self.waitingToStop = True

    def set_detection(self, detection):
        self.detection = detection

    def get_detection(self):
        return self.detection