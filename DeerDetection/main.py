import queue
import cv2


from gui_video_output import Gui_video_output
from processThread import ProcessThread
import pafy


class Main:
    def __init__(self, title, url):
        # Send the URL through the pipeline 
        self.gui = Gui_video_output(url)
        
        #intialize variable to hold current webcam video frame
        self.current_frame = None
        
        #create a queue to fetch and execute callbacks passed 
        #from background thread
        self.callback_queue = queue.Queue()
        
        #create a thread to fetch webcam feed video
        self.process_thread = ProcessThread(self.gui, self.callback_queue, url)
        
        #save attempts made to fetch webcam video in case of failure 
        self.get_input_attempts = 0
        
        #register callback for being called when GUI window is closed
        self.gui.root.protocol("WM_DELETE_WINDOW", self.on_gui_closing)
        
        #start video source
        self.start_video()
        
        #start fetching video
        self.fetch_source_video()
    
    def on_gui_closing(self):
        self.get_input_attempts = 51
        self.process_thread.stop()
        self.process_thread.join()
        self.process_thread.release_resources()
        
        self.gui.root.destroy()

    def start_video(self):
        self.process_thread.start()
        
    def fetch_source_video(self):
            try:
                #while True:
                #try to get a callback put by the process thread
                #if there is no callback and call_queue is empty
                #then this function will throw a Queue.Empty exception 
                callback = self.callback_queue.get_nowait()
                callback()
                self.get_input_attempts = 0
                #self.app_gui.root.update_idletasks()
                self.gui.root.after(70, self.fetch_source_video)
                    
            except queue.Empty:
                if (self.get_input_attempts <= 50):
                    self.get_input_attempts = self.get_input_attempts + 1
                    self.gui.root.after(100, self.fetch_source_video)

    
    
    def launch(self):
        self.gui.launch()
        
    def __del__(self):
        self.process_thread.stop()


# ## The Launcher Code For GUI

# In[10]:

if __name__ == "__main__":
        url = "https://www.youtube.com/watch?v=8SDm48ieYP8"

main = Main("Title", url)
main.launch()