
import threading
import cv2
import math
import time
import geocoder
import time

from PIL import Image, ImageTk

from gui.gui_output import Gui_output
from input_.input_handler import Input_handler
from setup.startup_setup import Setup
from mqtt.MQTT_Publisher import Mqtt_publisher
from mqtt.MQTT_Subscriber import Mqtt_subscriber
from config.config import configparser


# Global variables
newVideoSource = None
newModelSource = None
noInput = False
times = []

class Process(threading.Thread):
    """ Class where thread is running to get a frame from the input data and call processing functions on the frame """

    def __init__(self, gui, callback_queue, fps, videoSource, modelSource, forceReload_flag, captureDetection, captureFrequency, detectionThreshold, output_dim, headless_mode, resize_flag):
        """
        Initialize the thread
        :param gui: Instance of GUI
        :param callback_queue: Callback Queue
        :param int fps: FPS of input source
        :param str videoSource: String representation of videoSource URL or Path
        :param str modelSource: String representation of modelSource URL or Path
        :param bool forceReload_flag: Boolean flag if the application should reload the PyTorch cache
        :param bool captureDetection: Boolean flag if images of detections should be saved
        :param int captureFrequency: Minimum interval in seconds between saving each picture
        :param float detectionThreshold: Decides confidence threshold at which is considered a detection
        :param tuple output_dim: Tuple containing (Width, height)
        :param bool headless_mode: Boolean flag if application is running in headless mode
        :param bool resize_flag: Boolean flag if video output should be resized
        """
        # Call the super class constructor
        threading.Thread.__init__(self)

        # Initialize references to variables
        self.gui = gui
        self.callback_queue = callback_queue
        self.fps = int(700/math.floor(fps))         # Set delay a bit faster than frame time since we're processing the frames
        print(f'[SETUP] DELAY set to {self.fps}ms') # Convert float FPS number to INT for cv2 waitkey
                                                    # Floor vs roof, decided to use floor so we dont process more frames than we have
        self.videoSource = videoSource
        self.modelSource = modelSource
        self.forceReload = forceReload_flag
        self.captureDetection = captureDetection
        self.captureFrequency = captureFrequency
        self.detectionThreshold = detectionThreshold
        self.output_dim = output_dim
        self.headless_mode = headless_mode
        self.resize_flag = resize_flag

        # Default values
        self.rawFrame = None
        self.waitingToStop = False                  # Flag for if the process should stop
        self.runningStatus = False                  # Flag for current status of thread

        ipLocation = geocoder.ip('me')
        self.currentLocation = str(ipLocation.latlng) # Location based on the current IP-Adress
        self.currentTime = None
        self.detected_flag = None
        self.detectedCount = 0
        self.lowestConfidence = None
        self.highestConfidence = None
        

        

        self.mqtt_publisher = Mqtt_publisher()
        self.mqtt_subscriber = Mqtt_subscriber()
        self.mqtt_subscriber.launch()

        # Create an instance of the input data
        self.input_handler = Input_handler(self.videoSource, 
                                            self.modelSource, 
                                            self.forceReload, 
                                            self.captureDetection,
                                            self.captureFrequency,
                                            self.detectionThreshold)

        if not self.headless_mode:
            # Set initial save detecion flag
            self.gui.update_savingDetection_status(captureDetection)

    
    def run(self):
        """ The thread's run method which checks for new input sources,
        sends a frame to be scored, plotted and sent to GUI/MQTT Publisher"""
        global newVideoSource
        global newModelSource
        global noInput
        newModel_fromRemote = None
        
        while (True):
            if (self.waitingToStop):
                self.runningStatus = True
                break
            
            # Check if new remote source has been published
            newModel_fromRemote = self.mqtt_subscriber.get_mqtt_source()
            if newModel_fromRemote is not None:
                newModelSource = Setup.download_newDefaultmodel(newModel_fromRemote)


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
                self.mqtt_subscriber.reset_mqtt_source()
               
            # Get a frame and return value from the input_instance
            ret, self.current_frame, self.rawFrame = self.input_handler.read_current_frame()

            
            if(ret == False):
                # If the return value of the input_instance is false, display no_input
                noInput = True
                if not self.headless_mode:
                    self.gui.update_output_image(ImageTk.PhotoImage(Image.open('resources/media/image_no-input.jpg')))
                    self.gui.update_title_from_input_source('No input')
                    msg = 'NO INPUT FROM VIDEO SOURCE'
                    self.mqtt_publisher.publishMsg(msg,
                                                   self.currentTime,
                                                   self.currentLocation,
                                                   self.detected_flag,
                                                   self.detectedCount,
                                                   self.lowestConfidence,
                                                   self.highestConfidence)
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
            
            # Publish MQTT Message
            self.mqtt_publisher.publishDefault(self.currentTime,
                                self.currentLocation,
                                self.detected_flag,
                                self.detectedCount,
                                self.lowestConfidence,
                                self.highestConfidence)

            # Wait for delay until next iteration
            cv2.waitKey(self.fps)

    
    def score_label_send_to_output(self, current_frame, rawFrame, gui):
        """ Function where the current frame is processed by functions of the input_handler and sent to GUI and/or MQTT Publisher
        This function is used as callback and executed by the thread
        :param current_frame: The current frame of the video
        :param rawFrame: A raw frame which will be saved without plots
        :param gui: The GUI instance
        """
        global detected_flag
        global detectedCount
        global currentTime

        # For each iteration, reset values
        detected_flag = None
        detectedCount = 0
        start_time = time.time() # Start time for measuring performance

        if self.resize_flag:
            current_frame = self.input_handler.resize_frame(current_frame, self.output_dim)
        
        # Score the frame and get the labels and coordinates from the current frame
        labels, cord = self.input_handler.predict_with_model(current_frame)
        prediction = labels, cord

        # Plot bounding box and label to the frame
        frame, detected_flag, detectedCount, lowestConfidence, highestConfidence = self.input_handler.plot_frame(prediction, current_frame, rawFrame)

                                                                              
        # Elements to be sendt in a msg with MQTT Client                            # Location is gotten in the initialization
        self.currentTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())     # Timestamp attributed to when the image was recieved
        self.set_detected(detected_flag)                                            # Set detection status for MQTT
        self.set_detectedCount(detectedCount)                                       # Set counter for how many animals detected
        self.set_confidenceValue(lowestConfidence, highestConfidence)

        # Process the frame for output and update the GUI
        if not self.headless_mode:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)                          # Convert the frame to RGB
            output_image = Image.fromarray(frame)                                   # Convert the image from array to PIL in order to show it using tkinter
            output_image = ImageTk.PhotoImage(output_image)                         # Convert the image to a Tkinter compatible Image 

            gui.update_output_image(output_image)                                   # Update the output image with the current image
            gui.update_alarm_status(detected_flag)                                  # Update the current alarm status


        executionTime = (time.time() - start_time)*1000                             # End time for measuring performance in milliseconds
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
        """ Function to set detected :param bool detection: """
        self.detected_flag = detection

    def set_detectedCount(self, detectedCount):
        """ Function to set detectedCount :param int detectedCount: """
        self.detectedCount = detectedCount

    def set_confidenceValue(self, lowestConfidence, highestConfidence):
        """ Function to set confidence value for message
        :param float lowestConfidence: Lowest confidence value of the frame
        :param float highestConfidence: Highest confidence value of the frame
        """
        try:
            self.lowestConfidence = float("{:.2f}".format(lowestConfidence))
        except Exception:
            pass
        
        try:
            self.highestConfidence = float("{:.2f}".format(highestConfidence))
        except Exception:
            pass
        

    def get_detection(self):
        """ Function to get detected_flag """
        return self.detected_flag

    @staticmethod
    def getNewVideoSource():
        """ Function to get a new video source while running """
        global newVideoSource
        newVideoSource = Setup.setVideoSource()

    @staticmethod
    def getNewModelSource():
        """ Function to get a new model source while running """
        global newModelSource
        newModelSource = Setup.setModelSource()

    def getNewTitle(self):
        """ Function to get a new title from the video source while running """
        global newVideoSource
        self.gui.update_title_from_input_source(newVideoSource)


    def calculateAverageProcessingTime(self, executionTime):
        """ Function to measure execution time per frame, for optimization and testing purposes
        :param int executionTime: Time for a frame to be processed """
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