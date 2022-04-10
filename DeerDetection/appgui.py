import tkinter as tk
from output import Output
import cv2
from PIL import Image, ImageTk
from input import Input
import time

class AppGui:
    def __init__(self):
        #initialize the gui toolkit
        self.pred_instance = Input()
        self.root = tk.Tk()
        #set the geometry of the window
        #self.root.geometry("550x300+300+150")
        
        #set title of window
        self.root.title("Deer Detection")
        
        #create left screen view
        
        
        #create right screen view
        self.output_view = Output(self.root)
        self.output_view.pack(side='bottom')
        
        #define image width/height that we will use
        #while showing an image in webcam/neural network
        #output window
        self.image_width=200
        self.image_height=200
      
        self.is_ready = True
        
    def launch(self):
        #start the gui loop to listen for events
        self.root.mainloop()
        
    def process_image(self, image):
        #resize image to desired width and height
        #image = image.resize((self.image_width, self.image_height),Image.ANTIALIAS)
        image = cv2.resize(image, (360,360))
        
        #if image is RGB (3 channels, which means webcam image) then draw a circle on it
        #for user to focus on that circle to align face
        #if(len(image.shape) == 3):
        #    cv2.circle(image, self.circle_center, self.circle_radius, self.circle_color, 2)
        
        
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
        