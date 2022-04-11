from tkinter import*
import tkinter as tk

class Gui_Setup(tk.Frame):
    def __init__(self, root):
        #call super class (Frame) constructor
        tk.Frame.__init__(self, root)
        #save root layour for later references
        self.root = root
        #load all UI
        self.setup_ui()
        
    def setup_ui(self):

        #create label to hold image
        self.image_label = tk.Label(self)
        #put the image label inside top side screen
        self.image_label.pack(side="top", fill="both", expand="yes", padx=10, pady=10)

        self.alert = tk.Label(self.root, text="Alert Status") 
        #self.alert.config(bg="black") 
        self.alert.config(fg="black")
        self.alert.pack(padx=10, pady=10, fill="both", side="bottom")

        btn = tk.Button(self.root, text="Alert On!", command=self.alertOn)
        btn.pack(fill="both",side="bottom", expand=True, padx=10, pady=10)

        btn = tk.Button(self.root, text="Alert Off!", command=self.alertOff)
        btn.pack(fill="both", expand=True,side="bottom", padx=10, pady=10)

        #create output label
        self.output_label = tk.Label(self, text="Prediction output", bg="black", fg="white")
        self.output_label.pack(side="bottom", fill="both", expand="yes", padx=10)

        # create a button, that when pressed, will take the current frame and save it to file
        #btn = tk.Button(self.root, text="Snapshot!") #, command=self.take_snapshot
        #btn.pack(fill="both", expand=True, padx=10, pady=10)

        


         
        
    def update_image(self, image):
        #configure image_label with new image 
        self.image_label.configure(image=image)
        #this is to avoid garbage collection, so we hold an explicit reference
        self.image = image


    def alertOn(self):
        #self.alert = tk.Label(self.root, text="Alert Status: ACTIVE") 
        self.alert.config(bg="red")
        #self.detected = 1
        #self.detectedCheck()


     
    # -------------------------------------------------- x --------------------------------------------------

    def alertOff(self):
       #self.alert = tk.Label(self.root, text="Alert Status: NOT ACTIVE") 
        self.alert.config(bg="green")
        #self.detected = 0
        #self.detectedCheck()

    # -------------------------------------------------- x --------------------------------------------------

    def detectedCheck(self, detection):
        if detection:
            self.alertOn()
        else:
            self.alertOff()