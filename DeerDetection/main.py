import queue
import numpy as np

from gui_video_output import Gui_video_output
from processThread import ProcessThread


class Main:
    """ The main application class which is ran """ 

    def __init__(self, title, url):
        """ Initialization of the main class """ 
        
        # Initialize the GUI by calling the Gui_video_output
        self.gui = Gui_video_output()
        
        # Initialize variable to hold the current frame from the video output
        self.current_frame = None
        
        # Initialize a LastInn-FirstOut queue which will fetch and execute callbacks
        # Maxsize = 1 to ensure that the freshest frame is always the one processed and shown by the GUI
        self.callback_queue = queue.LifoQueue(maxsize = 1)
        
        # Initialize a thread which fetches the Video input
        self.process_thread = ProcessThread(self.gui, self.callback_queue, url)
           
        # Callback for when GUI window get's closed.
        self.gui.root.protocol("WM_DELETE_WINDOW", self.on_exit)
        
        # Initialize the delay in which the callback waits for re-execution
        self.callbackUpdateDelay = 33

        # Start the input source by calling the process thread
        self.start_input_source()
        
        # Start the callback loop
        self.callback_get_input()
    

    def launch(self):
        """ Function to launch the GUI """
        self.gui.launch()


    def start_input_source(self):
        """ Function to start the thread """ 
        self.process_thread.start()


    def callback_get_input(self):
            """ Callback function which listens for a new frame and executes """

            # Try to get a callback from the process thread
            try:
                self.callback_get_input
                
                # Empty the que
                callback = self.callback_queue.get_nowait()
                callback()
                    
            except queue.Empty:
                # If the que is empty, run the callback to get a frame
                self.gui.root.after(self.callbackUpdateDelay, self.callback_get_input)

            else: 
                self.gui.root.after(self.callbackUpdateDelay, self.callback_get_input)


    def on_exit(self):
        """ Function for closing the process when closing the GUI """

        # Stop the thread
        self.process_thread.stop()

        # Merge the threads
        self.process_thread.join()

        # Release the video resource
        self.process_thread.release_resources()
        
        # Destroy the GUI window
        self.gui.root.destroy()

        
    def __del__(self):
        """ Finalizer to stop the thread """ 
        self.process_thread.stop()



# Launch the program with the following parameters
if __name__ == "__main__":
        url = "https://www.youtube.com/watch?v=8SDm48ieYP8"

main = Main("Title", url)
main.launch()