import PIL.ImageTk
import tkinter as tk
import tkinter.filedialog
from videoprocessing import VideoProcessing

class sourceSelect(tk.Toplevel):

    # -------------------------------------------------- INIT --------------------------------------------------
    def __init__(self,parent, other_sources=None):
        super().__init__(parent)

        self.other_sources = other_sources
        print('[LOG] inputData - sourceSelect - init: ', self.other_sources)

        # default values at start
        self.item = None
        self.name = None
        self.source = None

        # GUI for selecting other file
        button = tk.Button(self, text="Open file...", command=self.on_select_file())
        button.pack(fill='both', expand=True)

        if self.other_sources:
            tk.Label(self, text="Other Sources:").pack(fill='both', expand=True)

            for item in self.other_sources:
                text, source = item
                button = tk.Button(self, text=text, command=lambda data=item:self.on_select_other(data))
                button.pack(fill='both', expand=True)



    # -------------------------------------------------- SOURCE SELECTION --------------------------------------------------
    # Select input data
    def on_select_file(self):
        """ TODO: Name not defined """
        result = tk.filedialog.askopenfilename(
                                        initialdir=".",
                                        title="Select video file",
                                        filetypes=(("MP4 files","*.mp4"), ("AVI files", "*.avi"), ("all files","*.*"))
                                    )
        print('[LOG] inputData - source_select - on_select_file: ', name, source)

    # Select training data
    def on_select_trainingData(self):
        result = tk.filedialog.askopenfilename(
                                        initialdir=".",
                                        title="Select training data",
                                        filetypes=(("all files","*.*"))
                                    )

        if result:
            self.item = item
            self.name = name # replace name with text?
            self.source = source

            print('[LOG] inputData - source_select - on_select_trainingData: ', name, source)
            self.destroy()
            self.dialog = None

    # Select other sources than those in the root directory
    def on_select_other(self, item):

        name, source = item

        self.item = item
        self.name = name
        self.source = source
      

        print('[LOG] inputData - source_select - on_select_other:', name, source)
        # self.destroy()
        self.dialog = None

    def open_file(self):
        file = askopenfile (mode = 'r', filetypes = [(("MP4 files","*.mp4"), ("AVI files", "*.avi"), ("all files","*.*"))])
        if file is not None:
            content = file.read()
            self.source = file



            # -------------------------------------------------- GUI --------------------------------------------------
# The main GUI frame
class tkCamera(tkinter.Frame):

    # Create the main gui frame with buttons and video feed
    def __init__(self, parent, text="", source=0, width=None, height=None, sources=None):

        super().__init__(parent)

        """ TODO: Fix correct source """ 
        self.source = source
        print('[LOG] inputData - tkCamera - init: source ', self.source)
        
        self.width  = width
        print('[LOG] inputData - tkCamera - init: width ', self.width)

        self.height = height
        print('[LOG] inputData - tkCamera - init: height ', self.height)

        self.other_sources = sources
        print('[LOG] inputData - tkCamera - init: other_sources: ', self.other_sources)

        #self.window.title(window_title)
        self.vid = VideoProcessing(self.source, self.width, self.height)
        print('[LOG] inputData - tkCamera - init: self.vid = VideoProcessing (source, w, h) ', self.vid)

        self.label = tk.Label(self, text=text)
        print('[LOG] inputData - tkCamera - init: self.label ', self.label)
        self.label.pack()

        self.canvas = tk.Canvas(self, width=self.vid.width, height=self.vid.height)
        print('[LOG] inputData - tkCamera - init: self.canvas ', self.canvas)
        self.canvas.pack()


        # -------------------------------------------------- BUTTONS  --------------------------------------------------
        # Button Video source
        self.btn_snapshot = tk.Button(self, text="Image Source", command=self.select_source)
        self.btn_snapshot.pack(anchor='center', side='left')

        # Button Alarm ON
        self.btn_snapshot = tk.Button(self, text="Manual: alarm ON", command=self.overrideAlarmOn)
        self.btn_snapshot.pack(anchor='center', side='left')

        # Button Alarm OFF
        self.btn_snapshot = tk.Button(self, text="Manual: alarm OFF", command=self.overrideAlarmOff)
        self.btn_snapshot.pack(anchor='center', side='left')


        # Button that lets the user take a snapshot
        self.btn_snapshot = tk.Button(self, text="Snapshot", command=self.snapshot)
        self.btn_snapshot.pack(anchor='center', side='left')


        # Button EXOT
        self.btn_snapshot = tk.Button(self, text="EXIT", command=self.exitProgram)
        self.btn_snapshot.pack(anchor='center', side='right')
 
        

        

        # After it is called once, the update method will be automatically called every delay milliseconds
        # calculate delay using `FPS`
        #self.delay = int(1000/self.vid.fps)
        """ TODO: Fix correct FPS read """
        self.delay = int(500)

        print('[LOG] source:', self.source)
        print('[LOG] fps:', self.vid.fps, 'delay:', self.delay)

        self.image = None

        self.dialog = None

        self.running = True

        self.update_frame()
        print('[LOG] inputData - tkCamera: frame updated') 
        






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
        print('[LOG] inputData - tkCamera: snapshot taken')

    # update the frame
    def update_frame(self):
        # widgets in tkinter already have method `update()` so I have to use different name -
        # Get a frame from the video source

        ret, frame = self.vid.get_frame()
        print('[LOG] inputData - tkCamera - update_frame: ', ret, frame)

        if ret:
            self.image = frame
            self.photo = PIL.ImageTk.PhotoImage(image=self.image)
            self.canvas.create_image(0, 0, image=self.photo, anchor='nw')
            # REDUCE SPAM print('[LOG] inputData - tkCamera - update_frame - if ret: ', ret)

        if self.running:
            self.after(self.delay, self.update_frame)
            # REDUCE SPAM print('[LOG] inputData - tkCamera - update_frame - if running: ', self.after)



    # Select source
    def select_source(self):
        self.dialog = sourceSelect(self, self.other_sources)

        self.label['text'] = self.dialog.name
        print('[LOG] inputData - tkCamera - select_source - label: ', self.label)

        self.source = self.dialog.source
        print('[LOG] inputData - tkCamera - select_source - source: ', self.source)

        self.vid = VideoProcessing(self.source, self.width, self.height)
        print('[LOG] inputData - tkCamera - select_source - self.vid: ', self.vid)



    


    # Select joblib dialogue
    def select_Joblib_source(self):
        
        # open only one dialog
        if self.dialog:
            print('[LOG] inputData - select_JobLib_source - Dialogue is already open')
            self.dialog.destroy()
        else:
            self.dialog = tkSourceSelect(self, self.other_sources)

            self.label['text'] = self.dialog.name
            self.source = self.dialog.source

    def overrideAlarmOn(self):
        print('Alarm ON')

    def overrideAlarmOff(self):
        print('Alarm OFF')

    def exitProgram(self):
        on_exit() # TODO 