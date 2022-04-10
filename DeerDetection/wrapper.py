import queue
import cv2


from appgui import AppGui
from processThread import ProcessThread


class Wrapper:
    def __init__(self):
        self.app_gui = AppGui()
        
        #create a Video camera instance
        #self.camera = VideoCamera()
        
        #intialize variable to hold current webcam video frame
        self.current_frame = None
        
        #create a queue to fetch and execute callbacks passed 
        #from background thread
        self.callback_queue = queue.Queue()
        
        #create a thread to fetch webcam feed video
        self.process_thread = ProcessThread(self.app_gui, self.callback_queue)
        
        #save attempts made to fetch webcam video in case of failure 
        self.get_input_attempts = 0
        
        #register callback for being called when GUI window is closed
        self.app_gui.root.protocol("WM_DELETE_WINDOW", self.on_gui_closing)
        
        #start webcam
        self.start_video()
        
        #start fetching video
        self.fetch_source_video()
    
    def on_gui_closing(self):
        self.get_input_attempts = 51
        self.process_thread.stop()
        self.process_thread.join()
        self.process_thread.release_resources()
        
        self.app_gui.root.destroy()

    def start_video(self):
        self.process_thread.start()
        
    def fetch_source_video(self):
            try:
                #while True:
                #try to get a callback put by webcam_thread
                #if there is no callback and call_queue is empty
                #then this function will throw a Queue.Empty exception 
                callback = self.callback_queue.get_nowait()
                callback()
                self.get_input_attempts = 0
                #self.app_gui.root.update_idletasks()
                self.app_gui.root.after(70, self.fetch_source_video)
                    
            except queue.Empty:
                if (self.get_input_attempts <= 50):
                    self.get_input_attempts = self.get_input_attempts + 1
                    self.app_gui.root.after(100, self.fetch_source_video)

    
    
    def launch(self):
        self.app_gui.launch()
        
    def __del__(self):
        self.process_thread.stop()


# ## The Launcher Code For GUI

# In[10]:

# if __name__ == "__main__":
wrapper = Wrapper()
wrapper.launch()