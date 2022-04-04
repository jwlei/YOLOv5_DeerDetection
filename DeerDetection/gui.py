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
        btnChangeImgSource["bg"] = "#e9e9ed"
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


        # Capture from camera
        cap = cv2.VideoCapture(0)

        # function for video streaming
        # Must create frame 
        def video_stream():
            _, frame = cap.read()
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            img = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=img)
            lmain.imgtk = imgtk
            lmain.configure(image=imgtk)
            lmain.after(1, video_stream) 

        

        video_stream()
        root.mainloop()

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


# widgets with canvas and camera

class tkCamera(tk.Frame):

    def __init__(self, window, video_source=0):
        super().__init__(window)
        
        self.window = window
        
        #self.window.title(window_title)
        self.video_source = video_source
        self.vid = MyVideoCapture(self.video_source)

        self.canvas = tk.Canvas(window, width=self.vid.width, height=self.vid.height)
        self.canvas.pack()
         
        # Button that lets the user take a snapshot
        self.btn_snapshot = tk.Button(window, text="Snapshot", width=50, command=self.snapshot)
        self.btn_snapshot.pack(anchor=tk.CENTER, expand=True)
         
        # After it is called once, the update method will be automatically called every delay milliseconds
        self.delay = 15
        self.update_widget()

    def snapshot(self):
        # Get a frame from the video source
        ret, frame = self.vid.get_frame()
        
        if ret:
            cv2.imwrite("frame-" + time.strftime("%d-%m-%Y-%H-%M-%S") + ".jpg", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
    
    def update_widget(self):
        # Get a frame from the video source
        ret, frame = self.vid.get_frame()
        
        if ret:
            self.image = pil.Image.fromarray(frame)
            self.photo = pil.ImageTk.PhotoImage(image=self.image)
            self.canvas.create_image(0, 0, image = self.photo, anchor = tk.NW)
        
        self.window.after(self.delay, self.update_widget)


class App:

    def __init__(self, window, window_title, video_source1=0, video_source2=0):
        self.window = window

        self.window.title(window_title)
        
        # open video source (by default this will try to open the computer webcam)
        self.vid1 = tkCamera(window, video_source1)
        self.vid1.pack()
        
        self.vid2 = tkCamera(window, video_source2)
        self.vid2.pack()
        
        # Create a canvas that can fit the above video source size
         
        self.window.mainloop()
     
    
     
class MyVideoCapture:
    def __init__(self, video_source=0):
        # Open the video source
        self.vid = cv2.VideoCapture(video_source)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)
    
        # Get video source width and height
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
    
        self.width = 400
        self.height = 300
    
    def get_frame(self):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret:
                frame = cv2.resize(frame, (400, 300))
                # Return a boolean success flag and the current frame converted to BGR
                return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            else:
                return (ret, None)
        else:
            return (ret, None)
    
    # Release the video source when the object is destroyed
    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()
 
# Create a window and pass it to the Application object
GUI(tk.Tk(), "Tkinter and OpenCV", 0, 'https://imageserver.webcamera.pl/rec/krupowki-srodek/latest.mp4')

if __name__ == "__main__":
    root = tk.Tk()
    app = GUI(root)
    root.mainloop()
