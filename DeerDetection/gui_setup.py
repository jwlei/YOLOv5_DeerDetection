import tkinter as tk
import os

from tkinter import font as tkFont



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
        titleLogo = tk.PhotoImage(file='media/logo_text_60px.png')
        self.logo = titleLogo
        

        # init UI
        self.setup_gui()

        
    def setup_gui(self):
        """
        Function for creating the GUI, defines buttons to create
        """
        helvetica = tkFont.Font(family="Helvetica", size=12)

        # Label for image
        
        self.titleLogo = tk.Label(self, image=self.logo)
        self.titleLogo.grid(row = 0, column = 0, columnspan = 1, sticky="NESW")

        self.titleLabel = tk.Label(self, font = helvetica, wraplength = 700)
        self.titleLabel.grid(row = 0, column = 1, columnspan = 3, padx=50, sticky="SE")

        self.video_output = tk.Label(self)
        self.video_output.grid(row = 1, column = 0, columnspan = 4,  padx=10, pady=10, sticky="NESW") # Position
        
        #self.video_output.pack_propagate(0) # Children fill the size

        # Detection indicator
        self.alert_status = tk.Label(self, text="Alert Status", fg="black")
        self.alert_status.config(bg = "orange")
        self.alert_status.grid(row = 2, column = 0, columnspan = 4, padx=10, sticky="NESW") # Position

        # Is saving detections indicator
        self.save_status = tk.Label(self, fg="black")
        self.save_status.config(text="Save on detection status")
        self.save_status.grid(row = 3, column = 0, columnspan = 1, padx=5, pady=10, sticky="NESW") # Position

        # Change video source
        self.sourceBtn = tk.Button(self, text="Choose video source", command=self.getNewVideoSource)
        self.sourceBtn.grid(row = 3, column = 1, columnspan = 1, padx=5, pady=10, sticky="NESW") # Position

        # Change model source
        self.sourceBtn = tk.Button(self, text="Choose training model", command=self.getNewModelSource)
        self.sourceBtn.grid(row = 3, column = 2, columnspan = 1,  padx=5, pady=10, sticky="NESW") # Position

        # Button Exit
        self.exitBtn = tk.Button(self, text="Exit program", command=self.on_exit)
        self.exitBtn.grid(row = 3, column = 3, columnspan = 1,  padx=5, pady=10, sticky="NESW") # Position 
        

    def update_source_title(self, title):
        """ Function to update the GUI with a new image """ 

        # Update the title label with a new title
        self.titleLabel.configure(text='Input source: '+ title)

        # Self reference to avoid garbage collection
        self.title = title

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