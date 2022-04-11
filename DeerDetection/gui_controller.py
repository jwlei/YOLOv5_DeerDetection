import tkinter as tk
import cv2
import time


from PIL import Image, ImageTk
from gui_setup import Gui_Setup
from input import Input


class Gui_Controller:
    def __init__(self, url): 
        #initialize the gui toolkit
        self.pred_instance = Input(url)
        self.root = tk.Tk()
   
        
        #set title of window
        self.root.title("Deer Detection")
        
        
        #create output UI
        self.output_view = Gui_Setup(self.root)
        self.output_view.pack(side='bottom')
        
        #define image width/height that we will use
        #while showing output image 
 
        self.image_width=640
        self.image_height=640
      
        self.is_ready = True
        
    def launch(self):
        #start the gui loop to listen for events
        self.root.mainloop()
        
    def process_image(self, image):
        #resize image to desired width and height
        #image = image.resize((self.image_width, self.image_height),Image.ANTIALIAS)
        image = cv2.resize(image, (self.image_width, self.image_height))

        results = self.pred_instance.score_frame(image)
        garbage = image = self.pred_instance.plot_boxes(results, image)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        #convert image to PIL library format which is required for Tk toolkit
        image = Image.fromarray(image)
        
        #convert image to Tk toolkit format
        image = ImageTk.PhotoImage(image)
        
        return image
        
    def update_output(self, image):
        #pre-process image to desired format, height etc.
        image = self.process_image(image)
        #pass the image to right_view to update itself
        self.output_view.update_image(image)
        