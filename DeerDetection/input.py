import cv2
import pafy
import torch
from time import time
import os

class Input:
    """ Class for supplying and manipulating input data """ 

    def __init__(self, videoSource, modelSource, forceReload):
        """ Initializing the input data stream """ 

        # Load the URL passed from the Main class
        self.videoSource = videoSource

        # Load the file passed from Main
        self.modelSource = modelSource

        self.forceReload = forceReload

        # Load the model defined in the load_model function
        self.model = self.load_model()

        # Load the classes defined in the model
        self.classes = self.model.names

        # Set the device for the model to load on to be the cuda device, otherwise the cpu
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'

        # Print the Device used for logging purposes
        print("\n\nDevice Used:",self.device)

        # Set default values
        # Boolean for successfully returned frame
        self.ret = False
        # Actual frame to be processed and output on the tkinter canvas
        self.frame = None
        # Set initial value for detection
        self.detection = False

        # Set the video source
        self.video_capture = self.input_settings(cv2.VideoCapture(videoSource))
        """
        # For testing purposes, uncomment to use a YouTube video link
        ytlink = self.get_video_from_url()
        self.video_capture = ytlink
        """
    
    def load_model(self):
        """ Function to load the YOLOv5 model from the pyTorch GitHub when not implemented locally """ 
        model = torch.hub.load('ultralytics/yolov5', 'custom', path=self.modelSource, force_reload=self.forceReload)
        
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


    def plot_frame(self, prediction, frame):
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

            # Set confidence threshold to predict on
            confidenceThreshold = 0.5

            # If confidence interval is greater than confidenceThreshold do:
            if row[4] >= confidenceThreshold:
                detection = True
                detectionCount = labelLength
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
        """ Function to get a single frame and it's return boolean value """ 

        # Get boolean return and frame from the video feed
        ret, frame = self.video_capture.read()

        return ret, frame


    def get_ytVideo_from_url(self):
        """ Function to process a youtube URL """

        ytLink = pafy.new(self.videoSource).streams[-1]
        assert ytLink is not None
        ytVideo = cv2.VideoCapture(ytLink.url)
        
        # Define constraints to the video

        return ytVideo
    
    def input_settings(self, video_capture):
        video_capture.set(cv2.CAP_PROP_BUFFERSIZE, 2)
        video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 100)
        video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 100)
        video_capture.set(cv2.CAP_PROP_FPS, 30)
      

        return video_capture

    def release(self):
        """ Function to manually release the resource """
        self.video_capture.release()

    def __del__(self):
        """ Function to release the resource """
        self.video_capture.release()
        
