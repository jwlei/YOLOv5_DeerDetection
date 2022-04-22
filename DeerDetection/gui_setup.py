from tkinter import*
import tkinter as tk
import os


class Gui_Setup(tk.Frame):
    """ Class to set up the initial GUI """ 

    def __init__(self, root, on_exit, getNewVideoSource, getNewModelSource):
        """ Initialization of the GUI_Setup class, which calls the setup_gui function to create the GUI """

        # Frame constructor from the super class
        tk.Frame.__init__(self, root)

        # Load passed from main
        self.on_exit = on_exit
        self.getNewVideoSource = getNewVideoSource
        self.getNewModelSource = getNewModelSource

        # layout reference
        self.root = root

        # init UI
        self.setup_gui()

        
    def setup_gui(self):
        """
        Function for creating the GUI, defines buttons to create
        """

        # Label for image
        self.video_output = tk.Label(self)
        self.video_output.pack(side="top", fill="both", expand="yes", padx=10, pady=10) # Position

        # Detection indicator
        self.alert_status = tk.Label(self, text="Alert Status", fg="black")
        self.alert_status.config(bg = "orange")
        self.alert_status.pack(side="top", fill="both", expand="yes", padx=10) # Position

        # Is saving detections indicator
        self.save_status = tk.Label(self, fg="black")
        self.save_status.config(text="Save on detection status")
        self.save_status.pack(side="left", fill="both", expand="yes", padx=10, pady=10) # Position

        # Change video source
        self.sourceBtn = tk.Button(self, text="Choose video source", command=self.getNewVideoSource)
        self.sourceBtn.pack(fill="both", expand=True, side="left", padx=10, pady=10) # Position

        # Change model source
        self.sourceBtn = tk.Button(self, text="Choose training model", command=self.getNewModelSource)
        self.sourceBtn.pack(fill="both", expand=True, side="left", padx=10, pady=10) # Position

        # Button Exit
        self.exitBtn = tk.Button(self, text="Exit program", command=self.on_exit)
        self.exitBtn.pack(fill="both", expand=True, side="left", padx=10, pady=10) # Position
        

    def update_gui_image(self, image):
        """ Function to update the GUI with a new image """ 

        # Update the image label with a new image
        self.video_output.configure(image=image)

        # Self reference to avoid garbage collection
        self.image = image

    # -------------------------------------------------- Button Functions --------------------------------------------------

    def alertDetected(self):
        # If detection, status: RED
        self.alert_status.config(bg="red")

    def alertNoDetection(self):
        # If no detection, status: GREEN
        self.alert_status.config(bg="green")

    def isSaving(self):
        # If detection, status: RED
        self.save_status.config(text="SAVING ON DETECTION", bg="red")

    def isNotSaving(self):
        # If no detection, status: GREEN
        self.save_status.config(text="NOT SAVING ON DETECTION", bg="green")



 
    def chooseVideoSource(self):
        # do change source
        #Main.chooseVideoSource()
        self.root.destroy()
        os.startfile('main.py')
       

    def chooseModelSource(self): 
        # do change source
        #Main.chooseModelSource()
        print('placeholder')

    def exit(self):
        # Do exit
        self
        print('placeholder')


    # -------------------------------------------------- Checks for deciding indicator status --------------------------------------------------

    def detectionIndicator(self, detection):
        """ Function for deciding the detection warning status """ 

        if detection:
            self.alertDetected()
        else:
            self.alertNoDetection()

    def savingIndicator(self, saveDetections):
        """ Function for deciding the detection warning status """ 

        if saveDetections:
            self.isSaving()
        else:
            self.isNotSaving()