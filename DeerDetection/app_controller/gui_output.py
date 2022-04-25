import tkinter as tk

from app_view.gui_setup import Gui_Setup



class Gui_output:
    """ Class for handling the updating of the GUI frame """ 

    def __init__(self, on_exit, sourceTitle, windowTitle, getNewVideoSource, getNewModelSource): 
        """ Initialization of the video output """ 

        #initialize the gui toolkit
        self.root = tk.Tk()
        
        # GUI Setup values
        self.root.title(windowTitle)
        #self.root.geometry(f'{device_w}x{device_h}')
        #device_w = int(self.root.winfo_screenwidth()/2)
        #device_h = int(self.root.winfo_screenheight()/2)
        

        # Initialize the Gui by calling the Gui_setup class
        self.output_view = Gui_Setup(self.root, on_exit, getNewVideoSource, getNewModelSource)
        self.output_view.pack(side='top')
        self.output_view.update_source_title(sourceTitle)

    
    def update_title_from_input_source(self, new_source_title):
        # Use the output_view image to update the image in the frame
        self.output_view.update_source_title(new_source_title)

    def update_output_image(self, output_image):
        # Use the output_view image to update the image in the frame
        self.output_view.update_gui_image(output_image)

    def update_alarm_status(self, detection_flag):
        # Use the output_view detection check value to update the alarm status of the GUI
        self.output_view.update_detectionIndicator(detection_flag)

    def update_savingDetection_status(self, saveDetections_flag):
        # Use the output_view detection check value to update the saving indicator of the GUI
        self.output_view.update_savingIndicator(saveDetections_flag)

    def launch(self):
        # Launch the GUI and listen for callback events
        self.root.mainloop()