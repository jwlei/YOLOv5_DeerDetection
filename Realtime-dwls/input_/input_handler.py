import os
import cv2
import pafy # pip install youtube-dl==2020.12.2
import torch
import time
import numpy as np


from pathlib import Path

class Input_handler:
    """ Class for supplying and manipulating input data """ 

    def __init__(self, videoSource, modelSource, forceReload_flag, saveDetections_flag, captureFrequency, detectionThreshold):
        """ Initializing the input data stream """ 

        # Load flags passed from main
        self.videoSource = videoSource
        self.modelSource = modelSource
        self.forceReload = forceReload_flag
        self.saveDetections_flag = saveDetections_flag
        self.captureFrequency = captureFrequency
        self.detectionThreshold = detectionThreshold
        

        
        self.model = self.load_model()                              # Load the model defined in the load_model function
        self.classes = self.model.names                             # Load the classes defined in the model
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu' # Set the device for the model to load on to be the cuda device, otherwise the cpu
        


        # Print the Device used for logging purposes
        print('[SETUP] Device Used: ',self.device)

        # Set default values
        
        self.ret = False                # Boolean for successfully returned frame
        self.frame = None               # Actual frame to be processed and output
        self.detected_flag = False      # Set initial value for detection

        
        self.startTime = time.time()    # Start time for interval deciding when to save a new picture
        self.savedImageCounter = 0      # Incremental counter which is appended to saved images' filename
        # TODO: Fix path?
        self.path = Path.cwd() / 'resources/SavedDetections'
        print('[SETUP] Saved RAW images will be saved to: ', self.path)
        

        # Process and set the videoSource
        self.processed_videoSource = self.processInputPath(videoSource)
        
       
        
        

    def load_model(self):
        """ Function to load the YOLOv5 model from the pyTorch GitHub when not implemented locally """ 
        model = torch.hub.load('ultralytics/yolov5', 
                                'custom', 
                                path=self.modelSource, 
                                force_reload=self.forceReload)
 
        return model
    

    def predict_with_model(self, frame):
        """ Function to score a frame with the model """ 

        self.model.to(self.device)                                                      # Send the model to the device

        frame = [frame]                                                                 # Assign the frame
        prediction = self.model(frame)                                                  # Score the frame on the model
     
        
        labels, coordinates = prediction.xyxyn[0][:, -1], prediction.xyxyn[0][:, :-1]   # Grab the labels and coordinates from the results
        return labels, coordinates


    def label_toString(self, x):
        """ Function to return the label of in which to assign to a score """ 
        return self.classes[int(x)]


    def plot_frame(self, prediction, frame, rawFrame):
        """ Function to plot boxes, labels and confidence values around detections on the frame """ 
        global detection_flag
        global detectionCount
        detection_flag = False
        detectionCount = 0
        highestConfidence = None
        lowestConfidence = None

        background_color = (0, 0, 255)                                                  # Color of the box
        text_color = (255, 255, 255)                                                    # Color of the 
        
        labels, coordinates = prediction                                                # Grab the labels and coordinates from the results 
        labelLength = len(labels)                                                       # Grab the length of the labels
        x_shape, y_shape = frame.shape[1], frame.shape[0]                               # Pass the shape of the box to be plot

        for i in range(labelLength):                                                    # For each label detected, plot the bounding box, label and confidence value
            row = coordinates[i]                                                        # Grab the prediction to plot
            confidenceValue = row[4]                                                    # Grab the confidence value from the tuple
            
            if confidenceValue >= self.detectionThreshold:                              # If confidence interval is greater than confidenceThreshold do:
                detection_flag = True
                detectionCount = labelLength

                if lowestConfidence is None or confidenceValue <= lowestConfidence:     # Get lowest confidence value from the image
                    lowestConfidence = confidenceValue

                if highestConfidence is None or confidenceValue >= highestConfidence:   # Get highest confidence value from the image
                    highestConfidence = confidenceValue
                
                
                
                self.save_raw_image(rawFrame)                                           # If enabled, save picture on detection

                x1, y1, x2, y2 = int(row[0]*x_shape), int(row[1]*y_shape), int(row[2]*x_shape), int(row[3]*y_shape) # Get the coordinates of the box to be plot
                
                
                cv2.rectangle(frame,(x1, y1), (x2, y2), background_color, 2)            # Plot bounding box
  
                w, h = 110, 15
                cv2.rectangle(frame, (x1, y1), (x1 + w, y1 - h),background_color,-1)    # Plot background box for label
                              

                cv2.putText(frame,                                                      # Plot the label text
                            self.label_toString(labels[i]).upper()+' '+str("%.2f" % confidenceValue.item()), 
                            (x1, y1-3), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, text_color, 1)

        return frame, detection_flag, detectionCount, lowestConfidence, highestConfidence


        
    def read_current_frame(self):
        """ Function to get a single frame, copy it for raw photo collection, and it's return boolean value """
        ret, frame = self.processed_videoSource.read()                                  # Get boolean return and frame from the video feed
        try:
            rawFrame = frame.copy()                                                     # Try to copy the frame
        except Exception:
            rawFrame = frame
        
        return ret, frame, rawFrame


    def processInputPath(self, videoSource):
        """ Function to process the video input and assign as a cv2 video object """
        try: 
            processedSource = cv2.VideoCapture(int(videoSource))                        # Try to check if input is a camera
            print('[SETUP] Input source is identified as a local camera ... ')
            return processedSource
        except Exception:
            if "youtube" in videoSource or "youtu.be" in videoSource:                   # If the video source path contains fragments of youtube video URL's, handle them as such
                print('[SETUP] URL supplied is a YouTube-link, processing ... ')        # Since cv2 won't capture video from a YouTube URL as-is.
                ytLink = pafy.new(videoSource).streams[-1]
                assert ytLink is not None
                processedSource = cv2.VideoCapture(ytLink.url)
                return processedSource
            else:
                processedSource = cv2.VideoCapture(videoSource)                         # Otherwise assign it
                return processedSource

        
       


    def save_raw_image(self, rawFrame, imgLabel=None):
        """ Function to save an image from the frame """
        global savedImageCounter
        global startTime
        capture_interval = 60-self.captureFrequency                                     # User defined interval at which is the minimum time between pictures
        
        if not imgLabel:
            current_time = time.strftime("%Y-%m-%d_%H-%M-%S", time.gmtime())
            imgLabel = f'detection-{current_time}_{self.savedImageCounter}.png' #.jpg   # Name the saved file by by date and image counter to avoid duplicates
            secondIterator = (60.0 - (time.time() - self.startTime) % 60.0)             

            if secondIterator <= capture_interval:                                      # Print image if detection and int(interval) seconds has passed
                cv2.imwrite(os.path.join(self.path, imgLabel), rawFrame)                # Save the image to disk
                self.savedImageCounter += 1                                             # Increment the counter
                self.startTime = time.time()                                            # Reset the start time for a new interval

    def resize_frame(self, frame, output_dim):
        """ Function to resize the frame """ 
        resized_frame = cv2.resize(frame, output_dim)

        return resized_frame

    def release(self):
        """ Function to manually release the resource """
        self.processed_videoSource.release()

    def __del__(self):
        """ Function to release the resource """
        self.processed_videoSource.release()
        
