import tkinter as tk
import tkinter.filedialog

class sourceSelect(tkinter.Toplevel):

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