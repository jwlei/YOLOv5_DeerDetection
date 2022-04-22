import cv2
import pafy
import torch
import time
from pathlib import Path
import os
import threading

class Input:
    """ Class for supplying and manipulating input data """ 

    def __init__(self, videoSource, modelSource, forceReload, captureDetection, detectionThreshold):
        """ Initializing the input data stream """ 

        # Load flags passed from main
        self.videoSource = videoSource
        self.modelSource = modelSource
        self.forceReload = forceReload
        self.captureDetection = captureDetection
        self.detectionThreshold = detectionThreshold
        

        # Load the model defined in the load_model function
        self.model = self.load_model()
        # Load the classes defined in the model
        self.classes = self.model.names
        # Set the device for the model to load on to be the cuda device, otherwise the cpu
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'

        # Print the Device used for logging purposes
        print('[SETUP] Device Used: ',self.device)

        # Set default values
        # Boolean for successfully returned frame
        self.ret = False
        # Actual frame to be processed and output on the tkinter canvas
        self.frame = None
        # Set initial value for detection
        self.detection = False

        # Set initial value imageSaving
        self.startTime = time.time()
        self.imgCounter = 0
        self.savedImageCounter = 0
        self.path = Path.cwd() / 'SavedDetections'
        print('[SETUP] Saved RAW images will be saved to: ', self.path)
        

        # Process and set the videoSource
        self.video_capture = self.processInputPath(videoSource)

    
    def load_model(self):
        """ Function to load the YOLOv5 model from the pyTorch GitHub when not implemented locally """ 
        try:
            model = torch.hub.load('ultralytics/yolov5', 'custom', path=self.modelSource, force_reload=self.forceReload)
        except Exception:
            model = torch.hub.load('ultralytics/yolov5', 'custom', path=self.modelSource, force_reload=True)
        
        # Set custom parameters for the model
        # Set confidence limit to 0.75
        #model.conf = 0.75
        return model
    
    def predict_with_model(self, frame):
        """ Function to score a frame with the model """ 

        # Send the model to the device
        self.model.to(self.device)

        # Assign the frame
        frame = [frame]

        # Score the frame on the model
        prediction = self.model(frame)
     
        # Grab the labels and coordinates from the results
        labels, coordinates = prediction.xyxyn[0][:, -1], prediction.xyxyn[0][:, :-1]
        
        return labels, coordinates


    def label_toString(self, x):
        """ Function to return the label of in which to assign to a score """ 

        return self.classes[int(x)]


    def plot_frame(self, prediction, frame, rawFrame):
        """ Function to plot boxes, labels and confidence values around detections on the frame """ 

        global detection

        global detectionCount
        detection = False
        detectionCount = 0

        # Color of the box
        background_color = (0, 0, 255)
        # Color of the text
        text_color = (0, 255, 0)

        # Grab the labels and coordinates from the results 
        labels, coordinates = prediction

        # Grab the length of the labels
        labelLength = len(labels)

        # Pass the shape of the box to be plot
        x_shape, y_shape = frame.shape[1], frame.shape[0]

        # For each label detected, plot the bounding box, label and confidence value
        for i in range(labelLength):

            # Grab the prediction to plot
            row = coordinates[i]

            # Grab the confidence value from the tuple
            confidenceValue = row[4]

            # If confidence interval is greater than confidenceThreshold do:
            if row[4] >= float(self.detectionThreshold):
                detection = True
                detectionCount = labelLength
                
                self.saveScreen(rawFrame)


                # Get the coordinates of the box to be plot
                x1, y1, x2, y2 = int(row[0]*x_shape), int(row[1]*y_shape), int(row[2]*x_shape), int(row[3]*y_shape)
                
                # Plot bounding box
                cv2.rectangle(frame, (x1, y1), (x2, y2), background_color, 2)

                # Plot label
                cv2.putText(frame, self.label_toString(labels[i]), (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 1.1, text_color, 4)

                # Plot confidence value
                cv2.putText(frame, str("%.2f" % confidenceValue.item()), (x2, y1), cv2.FONT_HERSHEY_SIMPLEX, 1.1, text_color, 4)
            else:
                detection = False

        return frame, detection, detectionCount


        
    def read_current_frame(self):
        """ Function to get a single frame, copy it for raw photo collection, and it's return boolean value """
        # Get boolean return and frame from the video feed
        # Try to copy the frame
        ret, frame = self.video_capture.read()
        try:
            rawFrame = frame.copy()
        except Exception:
            rawFrame = frame

        return ret, frame, rawFrame


    def processInputPath(self, videoSource):
        """ Function to process URL of video, if it's youtube process through PAFY """
        if "youtube" in videoSource or "youtu.be" in videoSource:
            print('[SETUP] URL supplied points to YouTube, processing ... ')
            ytLink = pafy.new(videoSource).streams[-1]
            assert ytLink is not None
            processedSource = cv2.VideoCapture(ytLink.url)
            return processedSource
        
        else:
            processedSource = cv2.VideoCapture(videoSource)
            return processedSource


    def saveScreen(self, rawFrame, imgLabel=None):
        """ Function to save an image from the frame """
        global savedImageCounter
        global startTime

        if not imgLabel:
           
            current_time = time.strftime("%Y-%m-%d_%H-%M-%S", time.gmtime())
            imgLabel = f'detection-{current_time}_{self.savedImageCounter}.jpg'
            self.imgCounter += 1
            secondIterator = (60.0 - (time.time() - self.startTime) % 60.0)
            

            # Print image if detection every 60 minus X seconds
            if secondIterator <= 54: # Current every 4 seconds EDIT THIS VALUE
                cv2.imwrite(os.path.join(self.path, imgLabel), rawFrame)
                self.savedImageCounter += 1
                self.startTime = time.time()
                


    def release(self):
        """ Function to manually release the resource """
        self.video_capture.release()

    def __del__(self):
        """ Function to release the resource """
        self.video_capture.release()
        
