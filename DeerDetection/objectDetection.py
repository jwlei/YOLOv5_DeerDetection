import os
import torch
import numpy as np
import cv2
import pafy
from time import time
import threading


class ObjectDetection:
    """
    Class implements Yolo5 model to make inferences on a youtube video using OpenCV.
    """
    od_frame = None
    def __init__(self): # - url
        """
        Initializes the class with youtube url and output file.
        :param url: Has to be as youtube URL,on which prediction is made.
        :param out_file: A valid output file name.
        """
        
        self._URL = "https://www.youtube.com/watch?v=3c4AOr40nQo"
        self._VIDEO = 'test.mp4'

        self.model = self.load_model()
        self.classes = self.model.names
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print("\n\nDevice Used:",self.device)
        

        
       
        ret = False
        frame = None
        
        

        #self.thread = threading.Thread(target=self.predict)
        #self.thread.start()

    def get_video_from_url(self):
        """
        Creates a new video streaming object to extract video frame by frame to make prediction on.
        :return: opencv2 video capture object, with lowest quality frame available for video.
        """
        
        #play = pafy.new(self._URL).streams[-1]
        #assert play is not None
        #return cv2.VideoCapture(play.url)

        play = self._VIDEO
        assert play is not None
        return cv2.VideoCapture(play)


    def load_model(self):
        """
        Loads Yolo5 model from pytorch hub.
        :return: Trained Pytorch model.
        """
        model = torch.hub.load('ultralytics/yolov5', 'custom', path='trainedModel_v1.pt', force_reload=False)
        return model


    def score_frame(self, frame):
        """
        Takes a single frame as input, and scores the frame using yolo5 model.
        :param frame: input frame in numpy/list/tuple format.
        :return: Labels and Coordinates of objects detected by model in the frame.
        """
        self.model.to(self.device)
        #print('[LOG] objectDetection - ObjectDetection - score_frame: Exported model to device')
        frame = [frame]
        results = self.model(frame)
     
        labels, cord = results.xyxyn[0][:, -1], results.xyxyn[0][:, :-1]
        return labels, cord


    def class_to_label(self, x):
        """
        For a given label value, return corresponding string label.
        :param x: numeric label
        :return: corresponding string label
        """
        return self.classes[int(x)]


    def plot_boxes(self, results, frame):
        """
        Takes a frame and its results as input, and plots the bounding boxes and label on to the frame.
        :param results: contains labels and coordinates predicted by model on the given frame.
        :param frame: Frame which has been scored.
        :return: Frame with bounding boxes and labels ploted on it.
        """
        labels, cord = results
        n = len(labels)
        x_shape, y_shape = frame.shape[1], frame.shape[0]
        for i in range(n):
            row = cord[i]
            if row[4] >= 0.2:
                x1, y1, x2, y2 = int(row[0]*x_shape), int(row[1]*y_shape), int(row[2]*x_shape), int(row[3]*y_shape)
                bgr = (0, 255, 0)
                cv2.rectangle(frame, (x1, y1), (x2, y2), bgr, 2)
                cv2.putText(frame, self.class_to_label(labels[i]), (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.9, bgr, 2)

        return frame


    def predict(self):
        global od_frame
        """
        This function is called when class is executed, it runs the loop to read the video frame by frame,
        and write the output into a new file.
        :return: void
        """
        player = self.get_video_from_url()
      
        assert player.isOpened()
        while True:  
            ret, frame = player.read()
            assert ret # TODO: If not ret, exit program
        
            frame = cv2.resize(frame, (416,416))
        
            start_time = time()
            results = self.score_frame(frame)
            garbage = frame = self.plot_boxes(results, frame)
            
            end_time = time()
            fps = 1/np.round(end_time - start_time, 2)
            #print(f"Frames Per Second : {fps}")
             
            cv2.putText(frame, f'FPS: {int(fps)}', (20,70), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,255,0), 2)
            
            cv2.imshow('YOLOv5 Detection', frame)
            garbagex = self.od_frame = frame
            print('[LOG] ObjectDetection - predict: od_frame', self.od_frame)
            return self.od_frame
            cv2.waitKey(333)
               

        
        #if True:
        #    self.after(1000, self.predict)
         
        player.release()
      
    


    #def get_od_frame(self):
        #return od_frame


            
            



# Create a new object and execute.
#detection = ObjectDetection()
#detection()