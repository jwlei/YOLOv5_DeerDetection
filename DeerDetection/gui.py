import tkinter as tk
import tkinter.font as tkFont

from PIL import ImageTk, Image as pil
import cv2

class GUI:
    def __init__(self, root):
        #setting title
        root.title("YOLOv5 Deer detection")
     

        #setting window size
        width=600
        height=500

        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()

        alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        root.geometry(alignstr)
        root.resizable(width=False, height=False)


        # Frame for image data
        frameDataFeed=tk.Button(root)
        frameDataFeed["bg"] = "#e9e9ed"
        ft = tkFont.Font(family='Calibri',size=10)
        frameDataFeed["font"] = ft
        frameDataFeed["fg"] = "#000000"
        frameDataFeed["justify"] = "center"
        frameDataFeed["text"] = "DATA FEED"
        frameDataFeed.place(x=20,y=20,width=552,height=332)
        frameDataFeed["command"] = self.framePlaceholder_command

        # Button configurations
        btnChangeImgSource=tk.Button(root)
        btnChangeImgSource["bg"] = "#e9e9ed"
        ft = tkFont.Font(family='Calibri',size=10)
        btnChangeImgSource["font"] = ft
        btnChangeImgSource["fg"] = "#000000"
        btnChangeImgSource["justify"] = "center"
        btnChangeImgSource["text"] = "Change image source"
        btnChangeImgSource.place(x=20,y=370,width=342,height=30)
        btnChangeImgSource["command"] = self.btnChangeImgSource_command

        btnChangeDataSource=tk.Button(root)
        btnChangeDataSource["bg"] = "#e9e9ed"
        ft = tkFont.Font(family='Calibri',size=10)
        btnChangeDataSource["font"] = ft
        btnChangeDataSource["fg"] = "#000000"
        btnChangeDataSource["justify"] = "center"
        btnChangeDataSource["text"] = "Change training model"
        btnChangeDataSource.place(x=20,y=410,width=342,height=30)
        btnChangeDataSource["command"] = self.btnChangeDataSource_command

        detectionIndicator=tk.Message(root)
        ft = tkFont.Font(family='Calibri',size=10)
        detectionIndicator["font"] = ft
        detectionIndicator["fg"] = "#333333"
        detectionIndicator["justify"] = "center"
        detectionIndicator["text"] = "Alarm indicator"
        detectionIndicator.place(x=410,y=370,width=171,height=116)

        btnManualOn=tk.Button(root)
        btnManualOn["bg"] = "#e9e9ed"
        ft = tkFont.Font(family='Calibri',size=10)
        btnManualOn["font"] = ft
        btnManualOn["fg"] = "#000000"
        btnManualOn["justify"] = "center"
        btnManualOn["text"] = "Manual: Alarm ON"
        btnManualOn.place(x=20,y=460,width=161,height=30)
        btnManualOn["command"] = self.btnManualOn_command

        btnManualOff=tk.Button(root)
        btnManualOff["bg"] = "#e9e9ed"
        ft = tkFont.Font(family='Calibri',size=10)
        btnManualOff["font"] = ft
        btnManualOff["fg"] = "#000000"
        btnManualOff["justify"] = "center"
        btnManualOff["text"] = "Manual: Alarm OFF"
        btnManualOff.place(x=200,y=460,width=160,height=30)
        btnManualOff["command"] = self.btnManualOff_command



    # Button commands
    def btnChangeImgSource_command(self):
        print("Prompt for choosing new image source")


    def btnChangeDataSource_command(self):
        print("Prompt for choosing new dataset")


    def btnManualOn_command(self):
        print("Alarm is now ON")


    def btnManualOff_command(self):
        print("Alarm is now OFF")

    def framePlaceholder_command(self):
        print("Placeholder for Source image")


    

 
if __name__ == "__main__":
    root = tk.Tk()
    app = GUI(root)
    root.mainloop()
