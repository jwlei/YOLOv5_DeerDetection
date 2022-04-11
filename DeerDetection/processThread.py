import threading
import input
import cv2
import numpy
import torch
import time

from PIL import Image, ImageTk

from gui_video_output import Gui_video_output
from input import Input

class ProcessThread(threading.Thread):
    def __init__(self, gui, callback_queue, url):
        #call super class (Thread) constructor
        threading.Thread.__init__(self)
        #save reference to callback_queue
        self.callback_queue = callback_queue
        self.url = url
        
        #save left_view reference so that we can update it
        self.gui = gui
        
        #set a flag to see if this thread should stop
        self.should_stop = False
        
        #set a flag to return current running/stop status of thread
        self.is_stopped = False
        self.detection = False
        
        #create a Video camera instance
        self.input_instance = Input(url)
        #self.localtime = time.localtime()
        
    #define thread's run method
    def run(self):
        #start the video feed
        while (True):

            #check if this thread should stop
            #if yes then break this loop
            if (self.should_stop):
                self.is_stopped = True
                break
            
            #read a video frame
            ret, self.current_frame = self.input_instance.read_image()
            
           # print('[LOG] processThread - run : Sleeping for ', self.FPS_MS)
            if(ret == False):
                print('Video capture failed')
                exit(-1)

            #cv2.waitKey(10)
            
            if self.callback_queue.full() == False:
                #put the update UI callback to queue so that main thread can execute it
                self.callback_queue.put((lambda: self.score_label_send_to_output(self.current_frame, self.gui)))

        
            
    #this method will be used as callback and executed by main thread
    def score_label_send_to_output(self, current_frame, gui):
        global detection
        detection = None
        

        #start_time = time() # FPS
        labels, cord = self.input_instance.score_frame(current_frame)
        scored_frame = labels, cord
        detection = self.checkLabel(labels)

        if detection:
            detection = True
        else:
            detection = False

        



        
      


        frame = self.input_instance.plot_boxes(scored_frame, current_frame)
        #end_time = time() # FPS

        
        #fps = 1/numpy.round(end_time - start_time, 2) # FPS
        #cv2.putText(frame, f'FPS: {int(fps)}', (20,70), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,255,0), 2) # FPS

        #convert to RGB
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        frame = cv2.resize(frame, (640, 480))

        #convert image to PIL library format which is required for Tk toolkit
        image = Image.fromarray(frame)
        
        #convert image to Tk toolkit format
        image = ImageTk.PhotoImage(image)

        gui.update_output(image)
        gui.update_alarm_status(detection)
    
    def checkLabel(self, labels):
        global detection
        if str(labels) == "tensor([], device='cuda:0')":
            detection = False
        else:
            detection = True
      

        #if labels == torch.Tensor[]

        return detection
        
    def __del__(self):
        self.input_instance.release()
            
    def release_resources(self):
        self.input_instance.release()
        
    def stop(self):
        self.should_stop = True