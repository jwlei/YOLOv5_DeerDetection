import pymsgbox
from tkinter import filedialog

class StartupSetup:

    def setManualOrAutomatic():
        """ Decide automatic or manual setup """ 
        ans = pymsgbox.confirm('Please choose Automatic or Manual setup', 'DeerDetection Setup', buttons = ['Automatic', 'Manual', 'Gather images'])
        return ans


    def setVideoSource():
        """ Choose local or remote video source """
        ans = pymsgbox.confirm('Please choose your source for video', 'Pick video source', buttons = ['URL', 'Local Media'])

        if ans == 'URL':
            input = pymsgbox.prompt('Input URL of video input')
        elif ans == 'Local Media':
            input = filedialog.askopenfilename(initialdir="/",title="Select video", filetypes=(("MP4 Files", ".mp4"), ("All files",".*")))

        return input

    def setLocalOrUserModel():
        ans = pymsgbox.confirm('Use default or user-defined model?', 'Selecting model', buttons = ['Default', 'User-defined'])
        return ans

    def setModelSource():
        """ Choose local model source """ 
        pymsgbox.alert('Choose model data (.pt)', 'Pick model source')
        model = filedialog.askopenfilename(initialdir="/",title="Select model", filetypes=(("PT Files", ".pt"), ("All files",".*")))

        return model


    def setForceReload():
        """ Choose force reload of pyTorch cache on or off """
        ans = pymsgbox.confirm('Reload the pyTorch cache', 'DeerDetection Setup', buttons = ['No', 'Yes'])

        if ans == 'Yes':
            reloadBoolean = True
        else:
            reloadBoolean = False

        return reloadBoolean


    def setCaptureDetection():
        """ Choose if detections should be captured """ 
        ans = pymsgbox.confirm('Save detection images?', 'DeerDetection Setup', buttons = ['Yes', 'No'])

        if ans == 'Yes':
            captureBoolean = True
        else:
            captureBoolean = False

        return captureBoolean

    def setDetectionThreshold():
        threshold = pymsgbox.prompt('Input detection confidence threshold (0.0-1.0)')

        return threshold

