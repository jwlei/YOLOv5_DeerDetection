import tkinter as tk
import os

from tkinter import font as tkFont



class Gui_Setup(tk.Frame):
    """ Class to set up the initial GUI """ 

    def __init__(self, root, on_exit, getNewVideoSource, getNewModelSource):
        """
        Initialization of the GUI_Setup class, which calls the setup_gui function to create the GUI

        :param root: Root instance of parent
        :param function on_exit: on_exit function for button command
        :param tunction getNewVideoSource: function for button to initiate getting a new source
        :param function getNewModelSource: function for button to initiate getting a new source
        """

        # Frame constructor from the super class
        tk.Frame.__init__(self, root)                    

        # Initialize references
        self.on_exit = on_exit
        self.getNewVideoSource = getNewVideoSource
        self.getNewModelSource = getNewModelSource
        
        # GUI layout references
        self.root = root
        titleLogo = tk.PhotoImage(file='resources/media/logo.png')
        self.logo = titleLogo
        
        # Start the GUI
        self.setup_gui()

        
    def setup_gui(self):
        """ Function for creating the GUI, defines buttons to create """
        helvetica = tkFont.Font(family="Helvetica", size=12)

        # Title logo image
        self.titleLogo = tk.Label(self, image=self.logo)
        self.titleLogo.grid(row = 0, 
                            column = 0, columnspan = 1,
                            padx=(15,0), pady=(5,0),
                            sticky="NESW")
        # Title source label
        self.source_title_label = tk.Label(self, font = helvetica, wraplength = 300)
        self.source_title_label.grid(row = 0, 
                             column = 1, columnspan = 3, 
                             padx=50, 
                             sticky="SE")
        # Output image
        self.video_output = tk.Label(self)
        self.video_output.grid(row = 1, 
                               column = 0, columnspan = 4,  
                               padx=10, pady=10, 
                               sticky="NESW")

        # Detection indicator
        self.alert_status = tk.Label(self, text="Waiting for input data", fg="black")
        self.alert_status.config(bg = "orange")
        self.alert_status.grid(row = 2, 
                               column = 0, columnspan = 4, 
                               padx=10, 
                               sticky="NESW")

        # Is saving detections indicator
        self.save_status = tk.Label(self, fg="black")
        self.save_status.grid(row = 3, 
                              column = 0, columnspan = 1, 
                              padx=(10, 5), pady=10, 
                              sticky="NESW") # Position

        # Change video source
        self.sourceBtn = tk.Button(self, text="Choose video source", command=self.getNewVideoSource)
        self.sourceBtn.grid(row = 3, 
                            column = 1, columnspan = 1, 
                            padx=5, pady=10, 
                            sticky="NESW") # Position

        # Change model source
        self.sourceBtn = tk.Button(self, text="Choose model source", command=self.getNewModelSource)
        self.sourceBtn.grid(row = 3, 
                            column = 2, columnspan = 1,  
                            padx=5, pady=10, 
                            sticky="NESW") # Position

        # Button Exit
        self.exitBtn = tk.Button(self, text="Exit program", command=self.on_exit)
        self.exitBtn.grid(row = 3, 
                          column = 3, columnspan = 1,  
                          padx=(5, 10), pady=10, 
                          sticky="NESW") # Position
       


    # -------------------------------------------------- Logic --------------------------------------------------
    def update_detectionIndicator(self, detection_flag):
        """ Function for deciding the detection warning status

        :param bool detection_flag: Indicator for detection """
        if detection_flag:
            self.alert_status.config(text = "DETECTED", 
                                     bg="red")
        else:
            self.alert_status.config(text = "NO DETECTIONS", 
                                     bg="green")


    def update_savingIndicator(self, savingDetections_flag):
        """ Function for deciding the detection warning status

        :param bool savingDetections_flag: Indicates if images of detections are saved
        """
        if savingDetections_flag:
            self.save_status.config(text="SAVING ON DETECTION", 
                                    bg="red")
        else:
            self.save_status.config(text="NOT SAVING ON DETECTION", 
                                    bg="green")


    def update_source_title(self, source_title):
        """ Function to update the GUI title label with a new title

        :param str source_title: Title of the input video source """

        self.source_title_label.configure(text='Input source: '+ source_title)
        self.source_title = source_title # Garbage reference


    def update_gui_image(self, output_image):
        """ Function to update the GUI image label with a new image

        :param output_image: The processed photo image that should be displayed on the GUI """

        self.video_output.configure(image=output_image)
        self.image = output_image # Garbage reference