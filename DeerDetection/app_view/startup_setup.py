import pymsgbox
import os
import requests
import shutil

from tkinter import filedialog



class Setup:

    def setManualOrAutomatic():
        """ Decide automatic or manual setup """ 
        ans = pymsgbox.confirm('Please choose Automatic or Manual setup', 'DeerDetection Setup', buttons = ['Automatic', 'Manual', 'Gather images'])
        return ans


    def setVideoSource():
        """ Choose local or remote video source """
        ans = pymsgbox.confirm('Please choose your source for video', 'Pick video source', buttons = ['URL', 'Local Media', 'Camera'])

        if ans == 'URL':
            input = pymsgbox.prompt('Input URL of video input')
        elif ans == 'Local Media':
            input = filedialog.askopenfilename(initialdir="resources/media",title="Select video", filetypes=(("MP4 Files", ".mp4"), ("All files",".*")))
        elif ans == 'Camera':
            input = '0'

        return input

  
    def setModelSource():
        """ Choose model source """
        ans = pymsgbox.confirm('Use default or user-defined model?', 'Selecting model', buttons = ['Default', 'User-defined'])
        if ans == 'User-defined':
            
            ans = pymsgbox.confirm('Local or remote model?', 'Selecting model', buttons = ['Local', 'URL'])

            if ans == 'Local':
                pymsgbox.confirm('Choose model data (.pt)', buttons = ['OK'])
                model = filedialog.askopenfilename(initialdir="resources/models/",title="Select model", filetypes=(("PT Files", ".pt"), ("All files",".*")))
                return model

            elif ans == 'URL':
                modelUrl = pymsgbox.prompt('Input URL of model')
                model = StartupSetup.downloadModel(modelUrl)
                return model

        elif ans == 'Default':
            return ans
            


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
        ans = pymsgbox.confirm('Save detection images?', 'DeerDetection Setup', buttons = ['Save', 'Don\'t save'])

        if ans == 'Yes':
            captureBoolean = True
        else:
            captureBoolean = False

        return captureBoolean


    def setDetectionThreshold():
        threshold = pymsgbox.prompt('Input detection confidence threshold (0.0-1.0)')

        return threshold


    def downloadModel(modelUrl):
        """ Save supplied Model URL to disk """ 
        path = 'resources/models/'
        filenameFromUrl = modelUrl.rpartition('/')[-1]
        path_to_check = os.path.join(path, filenameFromUrl)
        # Check if file already exists
        file_exists = os.path.exists(path_to_check)

        # If the file already exists, allow the user to assign a custom name to the downloaded model
        if file_exists: 
            user_defined_filename = pymsgbox.prompt(f'A model named {filenameFromUrl} already exists, please rename the model.')
            if not '.pt' in user_defined_filename:
                filename = user_defined_filename+'.pt'
            if '.pt' in user_defined_filename:
                filename = user_defined_filename   
        else:
            filename = filenameFromUrl

        path_filename = os.path.join(path, filename)

        # Download the file and save to disk 
        r = requests.get(modelUrl, stream=True)
  
        with requests.get(modelUrl, stream=True) as r:
            with open(path_filename, 'wb') as file:
                print('[SETUP] Downloading remote model file ... ')
                shutil.copyfileobj(r.raw, file)
                    
        print('[SETUP] '+filename+' download complete and saved to '+path)

        return path_filename
        
        
                
                

