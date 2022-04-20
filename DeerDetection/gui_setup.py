from tkinter import*
import tkinter as tk

class Gui_Setup(tk.Frame):
    """ Class to set up the initial GUI """ 

    def __init__(self, root):
        """
        Initialization of the GUI_Setup class, which calls the setup_gui function to create
        the GUI
        """

        # Frame constructor from the super class
        tk.Frame.__init__(self, root)

        # layout reference
        self.root = root
        
        # init UI
        self.setup_gui()
        
    def setup_gui(self):
        """
        Function for creating the GUI, defines buttons to create
        """

        # TODO: comment btns
        # Label for image
        self.image_label = tk.Label(self)
        self.image_label.pack(side="top", fill="both", expand="yes", padx=10, pady=10) # Position

        self.alert = tk.Label(self.root, text="Alert Status") 
        self.alert.config(fg="black")
        self.alert.pack(padx=10, pady=10, fill="both", side="bottom") # Position

        alarmBtn = tk.Button(self.root, text="Manual: Alert On!", command=self.alertOn)
        alarmBtn.pack(fill="both",side="bottom", expand=True, padx=10, pady=10) # Position

        alarmBtn = tk.Button(self.root, text="Manual: Alert Off!", command=self.alertOff)
        alarmBtn.pack(fill="both", expand=True,side="bottom", padx=10, pady=10) # Position

        # TODO: Exit button
        #exitBtn = tk.Button(self.root, text="Exit program", command=self.exit)
        #exitBtn.pack(fill="both", expand=True,side="bottom", padx=10, pady=10) # Position

        # Banner 
        self.output_label = tk.Label(self, text="Prediction output", bg="black", fg="white")
        self.output_label.pack(side="bottom", fill="both", expand="yes", padx=10) # Position

        # TODO: Implement snapshot saving on detection?
        # create a button, that when pressed, will take the current frame and save it to file
        #btn = tk.Button(self.root, text="Snapshot!") #, command=self.take_snapshot
        #btn.pack(fill="both", expand=True, padx=10, pady=10)

        
    def update_gui_image(self, image):
        """ Function to update the GUI with a new image """ 

        # Update the image label with a new image
        self.image_label.configure(image=image)

        # Self reference to avoid garbage collection
        self.image = image


    # -------------------------------------------------- Button Functions --------------------------------------------------

    def alertOn(self):
        #self.alert = tk.Label(self.root, text="Alert Status: ACTIVE") 
        self.alert.config(bg="red")
        #self.detected = 1
        #self.detectedCheck()

    def alertOff(self):
       #self.alert = tk.Label(self.root, text="Alert Status: NOT ACTIVE") 
        self.alert.config(bg="green")
        #self.detected = 0
        #self.detectedCheck()

    # TODO: Exit button
    #def exit(self):


    # -------------------------------------------------- Logic for deciding detection warning --------------------------------------------------

    def detectedCheck(self, detection):
        """ Function for deciding the detection warning status """ 

        if detection:
            self.alertOn()
        else:
            self.alertOff()