import os
import tkinter as tk
import cv2
from inputData import tkCamera

HOME = os.path.dirname(os.path.abspath(__file__))

class Main: 
    # -------------------------------------------------- INIT --------------------------------------------------
    # Initialize the main window

    def __init__(self, parent, title, sources):
        self.parent = parent
        self.parent.title(title)
        # TODO: Check if widget is actually correct and running inputData
        self.stream_widgets = []

        #Dimensions
        width = 1028
        height = 768

        columns = 2
        for number, (text, source) in enumerate(sources):
            widget = tkCamera(self.parent, text, source, width, height, sources)
            row = number // columns
            col = number % columns
            widget.grid(row=row, column=col)
            self.stream_widgets.append(widget)

            # OLD print('[LOG] main - Main: cv2 path: ' + cv2.__file__)

        #widget = tkCamera(self.parent, source, width, height)
            self.parent.protocol("WM_DELETE_WINDOW", self.on_exit)


    def on_exit(self, event=None):
        for widget in self.stream_widgets:
            print('[LOG] main - Main: Stopping threads')
            widget.vid.running = False

        print('[LOG] main - main EXIT')
        self.parent.destroy()

if __name__ == "__main__":
    #          ("text", "source")
    sources = [("Big Buck Bunny", "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"),
               ("For Bigger Blazes", "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4")
               ]

root = tk.Tk()
Main(root, "Deer detection v2", sources)
root.mainloop()