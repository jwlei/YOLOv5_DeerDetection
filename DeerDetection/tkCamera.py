import PIL.ImageTk
import tkinter as tk
import tkinter.filedialog
from videocapture import VideoCapture


class tkSourceSelect(tkinter.Toplevel):

    # -------------------------------------------------- INIT --------------------------------------------------
    def __init__(self, parent, other_sources=None):

        super().__init__(parent)

        self.other_sources = other_sources

        # default values at start
        self.item = None
        self.name = None
        self.source = None

        # GUI
        button = tkinter.Button(self, text="Open file...", command=self.on_select_file)
        button.pack(fill='both', expand=True)

        if self.other_sources:
            tkinter.Label(self, text="Other Sources:").pack(fill='both', expand=True)

            for item in self.other_sources:
                text, source = item
                button = tkinter.Button(self, text=text, command=lambda data=item:self.on_select_other(data))
                button.pack(fill='both', expand=True)



    # -------------------------------------------------- SOURCE SELECTION --------------------------------------------------
    # Select input data
    def on_select_file(self):
        result = tkinter.filedialog.askopenfilename(
                                        initialdir=".",
                                        title="Select video file",
                                        filetypes=(("MP4 files","*.mp4"), ("AVI files", "*.avi"), ("all files","*.*"))
                                    )

       
    

    # Select training data
    def on_select_trainingData(self):
        result = tkinter.filedialog.askopenfilename(
                                        initialdir=".",
                                        title="Select training data",
                                        filetypes=(("all files","*.*"))
                                    )

        if result:
            self.item = item
            self.name = name
            self.source = source

            print('[LOG] selected joblib source:', name, source)
            self.destroy()

    # Select other sources than those in the root directory
    def on_select_other(self, item):

        name, source = item

        self.item = item
        self.name = name
        self.source = source

        print('[LOG] selected other source:', name, source)

        self.destroy()



# -------------------------------------------------- GUI --------------------------------------------------
# The main GUI frame
class tkCamera(tkinter.Frame):

    # Create the main gui frame with buttons and video feed
    def __init__(self, parent, text="", source=0, width=768, height=1028, sources=None):

        super().__init__(parent)

        self.source = source
        self.width  = width
        self.height = height
        self.other_sources = sources

        #self.window.title(window_title)
        self.vid = VideoCapture(self.source, self.width, self.height)

        self.label = tk.Label(self, text=text)
        self.label.pack()

        self.canvas = tk.Canvas(self, width=self.vid.width, height=self.vid.height)
        self.canvas.pack()

        # Button Video source
        self.btn_snapshot = tk.Button(self, text="Image Source", command=self.select_source)
        self.btn_snapshot.pack(anchor='center', side='left')

        # Button Joblib source
        self.btn_snapshot = tk.Button(self, text="Joblib Source", command=self.select_Joblib_source)
        self.btn_snapshot.pack(anchor='center', side='right')

        # Button Alarm ON
        self.btn_snapshot = tk.Button(self, text="Manual: alarm ON", command=self.overrideAlarmOn)
        self.btn_snapshot.pack(anchor='center', side='left')

        # Button Alarm OFF
        self.btn_snapshot = tk.Button(self, text="Manual: alarm OFF", command=self.overrideAlarmOff)
        self.btn_snapshot.pack(anchor='center', side='left')


        # Button that lets the user take a snapshot
        self.btn_snapshot = tk.Button(self, text="Snapshot", command=self.snapshot)
        self.btn_snapshot.pack(anchor='center', side='left')
 
        

        

        # After it is called once, the update method will be automatically called every delay milliseconds
        # calculate delay using `FPS`
        #self.delay = int(1000/self.vid.fps)
        self.delay = int(1000/30)

        print('[LOG] source:', self.source)
        print('[LOG] fps:', self.vid.fps, 'delay:', self.delay)

        self.image = None

        self.dialog = None

        self.running = True
        self.update_frame()






# -------------------------------------------------- COMMANDS -------------------------------------------------- 
    # Button command for snapshot
    def snapshot(self):

        #Get a frame from the video source
        #ret, frame = self.vid.get_frame()
        #if ret:
        #    cv2.imwrite(time.strftime("frame-%d-%m-%Y-%H-%M-%S.jpg"), cv2.cvtColor(self.frame, cv2.COLOR_RGB2BGR))

        # Save current frame in widget - not get new one from camera - so it can save correct image when it stoped
        #if self.image:
        #    self.image.save(time.strftime("frame-%d-%m-%Y-%H-%M-%S.jpg"))

        self.vid.snapshot()

    # update the frame
    def update_frame(self):
        # widgets in tkinter already have method `update()` so I have to use different name -
        # Get a frame from the video source

        ret, frame = self.vid.get_frame()

        if ret:
            self.image = frame
            self.photo = PIL.ImageTk.PhotoImage(image=self.image)
            self.canvas.create_image(0, 0, image=self.photo, anchor='nw')

        if self.running:
            self.after(self.delay, self.update_frame)

    def select_source(self):
        self.dialog = tkSourceSelect(self, self.other_sources)

        self.label['text'] = self.dialog.name
        self.source = self.dialog.source
        self.update_frame()

            #self.vid = MyVideoCapture(self.source, self.width, self.height)
    


    # Select joblib dialogue
    def select_Joblib_source(self):
        #TODO Fix joblib source
        # open only one dialog
        if self.dialog:
            print('[LOG] Dialogue is already open')
        else:
            self.dialog = tkSourceSelect(self, self.other_sources)

            self.label['text'] = self.dialog.name
            self.source = self.dialog.source

    def overrideAlarmOn(self):
        print('Alarm ON')

    def overrideAlarmOff(self):
        print('Alarm OFF')
