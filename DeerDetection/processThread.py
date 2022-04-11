import threading
import input
import cv2
import time

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
        
        #create a Video camera instance
        self.camera = Input(url)
        
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
            ret, self.current_frame = self.camera.read_image()
            
           # print('[LOG] processThread - run : Sleeping for ', self.FPS_MS)
            if(ret == False):
                print('Video capture failed')
                exit(-1)

            #cv2.waitKey(10)
            
            if self.callback_queue.full() == False:
                #put the update UI callback to queue so that main thread can execute it
                self.callback_queue.put((lambda: self.update_on_main_thread(self.current_frame, self.gui)))

           
        
        #fetching complete, let's release camera
        #self.camera.release()
        
            
    #this method will be used as callback and executed by main thread
    def update_on_main_thread(self, current_frame, gui):
        gui.update_output(current_frame)
        prediction = Input.predict(current_frame)
        gui.update_output(prediction)

        
    def __del__(self):
        self.camera.release()
            
    def release_resources(self):
        self.camera.release()
        
    def stop(self):
        self.should_stop = True