import tkinter as tk

from gui_setup import Gui_Setup
from input import Input


class Gui_video_output:
    """ Class for handling the updating of the GUI frame """ 

    def __init__(self, on_exit, getNewVideoSource, getNewModelSource, sourceTitle): 
        """ Initialization of the video output """ 

        #initialize the gui toolkit
        self.root = tk.Tk()
   
        # Window Title
        self.root.title("Deer Detection")
        # (index, weight) 
        
        
        # Initialize the Gui by calling the Gui_setup class
        self.output_view = Gui_Setup(self.root, on_exit, getNewVideoSource, getNewModelSource)
        self.output_view.pack(side='top')
        self.output_view.update_source_title(sourceTitle)

    
    def update_title(self, title):
        # Use the output_view image to update the image in the frame
        self.output_view.update_source_title(title)

    def update_output_image(self, image):
        # Use the output_view image to update the image in the frame
        self.output_view.update_gui_image(image)

    def update_alarm_status(self, detection):
        # Use the output_view detection check value to update the alarm status of the GUI
        self.output_view.detectionIndicator(detection)

    def update_savingDetection_status(self, saveDetections):
        # Use the output_view detection check value to update the saving indicator of the GUI
        self.output_view.savingIndicator(saveDetections)

    def launch(self):
        # Launch the GUI and listen for callback events
        self.root.mainloop()