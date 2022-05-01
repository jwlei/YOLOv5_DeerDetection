import tkinter as tk

from setup.gui_setup import Gui_Setup



class Gui_output:
    """ Class for handling the updating of the GUI frame """ 

    def __init__(self, on_exit, sourceTitle, windowTitle, getNewVideoSource, getNewModelSource): 
        """
        Initialization of the video output
        :param function on_exit: The on_exit function to stop the application
        :param str sourceTitle: The source URL/Path of the video output
        :param str windowTitle: Window title depending on setup option
        :param str getNewVideoSource: Function to pass to the GUI for get a new source
        :param str getNewModelSource: Function to pass to the GUI for get a new source
        """

        #initialize the gui toolkit
        self.root = tk.Tk()

        # GUI Setup values
        self.root.title(windowTitle)
        # Initialize the Gui by calling the Gui_setup class
        self.output_view = Gui_Setup(self.root, on_exit, getNewVideoSource, getNewModelSource)
        self.output_view.pack()
        self.output_view.update_source_title(sourceTitle)

    
    def update_title_from_input_source(self, new_source_title):
        """ Use the output_view image to update the image in the frame
        :param str new_source_title: New title from selected source
        """
        self.output_view.update_source_title(new_source_title)

    def update_output_image(self, output_image):
        """ Use the output_view image to update the image in the frame
        :param output_image: PIL.Image
        """
        self.output_view.update_gui_image(output_image)

    def update_alarm_status(self, detection_flag):
        """ Use the output_view detection check value to update the alarm status of the GUI
        :param bool detection_flag: Indicates detection
        """
        self.output_view.update_detectionIndicator(detection_flag)

    def update_savingDetection_status(self, captureDetection):
        """ Use the output_view detection check value to update the saving indicator of the GUI
        :param bool captureDetection: Indicates if images of detections are saved
        """
        self.output_view.update_savingIndicator(captureDetection)

    def launch(self):
        """ Launch the GUI and listen for callback events """
        self.root.mainloop()