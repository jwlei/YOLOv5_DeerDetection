import os
import tkinter as tk
import cv2
from inputData import tkCamera

HOME = os.path.dirname(os.path.abspath(__file__))

class Main: 
    # -------------------------------------------------- INIT --------------------------------------------------
    # Initialize the main window

    def __init__(self, parent, title, widget):
        self.parent = parent
        self.parent.title(title)
        self.widget = widget

        #Dimensions
        width = 1028
        height = 768

        print('[LOG] cv2 path: ' + cv2.__file__)

        widget = tkCamera(self.parent, source, width, height)
        

        def on_exit(self, event=None):
            print('[LOG] Stopping threads')
            widget.vid.running = False

        self.parent.destroy()

if __name__ == "__main__":

    source = "Hytte View", "https://cameraftpapi.drivehq.com/api/camera/DF.aspx?sesID=rlkgs2z4ktmcdqshnogzgtld&isGallery=&share=true&shareID=17150495&fileID=8999618763&outputErrorInHeader=true&a.mp4"

root = tk.Tk()
Main(root, "Deer detection v2", source)
root.mainloop()