import pymsgbox
from tkinter import filedialog

class SourceSelect:

    def manualOrAutomatic():
        ans = pymsgbox.confirm('Please choose Automatic or Manual setup', 'DeerDetection Setup', buttons = ['Automatic', 'Manual'])
        return ans

    def chooseVideoSource():
        ans = pymsgbox.confirm('Please choose your source for video', 'Pick video source', buttons = ['URL', 'Local Media'])

        if ans == 'URL':
            input = pymsgbox.prompt('Input URL of video input')
        elif ans == 'Local Media':
            input = filedialog.askopenfilename(initialdir="/",title="Select video", filetypes=(("MP4 Files", ".mp4"), ("All files",".*")))

        return input

    def chooseModelSource():
        pymsgbox.alert('Choose model data (.pt)', 'Pick model source')
        model = filedialog.askopenfilename(initialdir="/",title="Select model", filetypes=(("PT Files", ".pt"), ("All files",".*")))

        return model

    def chooseForceReload():
        ans = pymsgbox.confirm('Reload the pyTorch cache', 'DeerDetection Setup', buttons = ['Yes', 'No'])

        if ans == 'Yes':
            reloadBoolean = True
        else:
            reloadBoolean = False

        return reloadBoolean