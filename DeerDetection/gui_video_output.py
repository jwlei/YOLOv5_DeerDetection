import tkinter as tk
import cv2
from PIL import Image, ImageTk

from gui_setup import Gui_Setup
from input import Input


class Gui_video_output:
    def __init__(self): 
        #initialize the gui toolkit
        self.root = tk.Tk()
   
        #set title of window
        self.root.title("Deer Detection")
        
        #create output UI
        self.output_view = Gui_Setup(self.root)
        self.output_view.pack(side='bottom')
        
        #define image width/height that we will use
        #while showing output image 

      
        self.is_ready = True
        
    def launch(self):
        #start the gui loop to listen for events
        self.root.mainloop()

    def update_output(self, image):
        #pass the image to output_view_image to update itself
        self.output_view.update_image(image)