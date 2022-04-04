import os
import tkinter as tk
from tkCamera import tkCamera

HOME = os.path.dirname(os.path.abspath(__file__))


class App:
    # -------------------------------------------------- INIT --------------------------------------------------
    def __init__(self, parent, title, sources):

        self.parent = parent

        self.parent.title(title)

        self.stream_widgets = []

        width = 1028
        height = 768

        #Multi cam view
        columns = 1
        for number, (text, source) in enumerate(sources):
            widget = tkCamera(self.parent, text, source, width, height, sources)
            row = number // columns
            col = number % columns
            widget.grid(row=row, column=col)
            self.stream_widgets.append(widget)

        self.parent.protocol("WM_DELETE_WINDOW", self.on_closing)


    # -------------------------------------------------- ON-EXIT --------------------------------------------------
    def on_closing(self, event=None):

        print("[LOG] stoping threads")
        for widget in self.stream_widgets:
            widget.vid.running = False

        print("[LOG] exit")
        self.parent.destroy()


if __name__ == "__main__":

    sources = [  
        # (text, source)
        (
            "Hytte view",
            "https://cameraftpapi.drivehq.com/api/camera/DF.aspx?sesID=rlkgs2z4ktmcdqshnogzgtld&isGallery=&share=true&shareID=17150495&fileID=8999618763&outputErrorInHeader=true&a.mp4"
        ),
         (
            "Zakopane, Poland",
            "https://imageserver.webcamera.pl/rec/krupowki-srodek/latest.mp4"
        )
    ]

    root = tk.Tk()
    App(root, "Deer detection v 0.1", sources)
    root.mainloop()