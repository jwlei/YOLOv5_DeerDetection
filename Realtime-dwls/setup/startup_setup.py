import pymsgbox
import os
import requests
import shutil
import configparser
import time

from tkinter import filedialog



class Setup:

    @staticmethod
    def setManualOrAutomatic():
        """ Decide automatic or manual setup
        :returns: str """
        ans = pymsgbox.confirm('Please choose Automatic or Manual setup', 
                               'DWLS Setup',
                               buttons = ['Automatic', 'Manual', 'Gather images'])
        return ans

    @staticmethod
    def setVideoSource():
        """ Choose local or remote video source
        :returns: str """
        input = None
        ans = pymsgbox.confirm('Please choose your source for video', 
                               'Pick video source', 
                               buttons = ['URL', 'Local Media', 'Camera'])

        if ans == 'URL':
            input = pymsgbox.prompt('Input URL of video input')
        elif ans == 'Local Media':
            input = filedialog.askopenfilename(initialdir="resources/media",
                                               title="Select video", 
                                               filetypes=(("MP4 Files", ".mp4"), ("All files",".*")))
        elif ans == 'Camera':
            input = pymsgbox.prompt('Enter camera ID, default is 0')

        return input

    @staticmethod
    def setModelSource():
        """ Choose model source
        :returns: str """
        ans = pymsgbox.confirm('Use default or user-defined model?', 
                               'Selecting model', 
                               buttons = ['Default', 'User-defined'])

        if ans == 'User-defined':
            ans = pymsgbox.confirm('Local or remote model?', 
                                   'Selecting model', 
                                   buttons = ['Local', 'URL'])

            if ans == 'Local':
                model = filedialog.askopenfilename(initialdir="resources/models/",
                                                   title="Select model (.pt)", 
                                                   filetypes=(("PT Files", ".pt"), ("All files",".*")))
                return model

            elif ans == 'URL':
                modelUrl = pymsgbox.prompt('Input URL of model')
                model = Setup.downloadModel(modelUrl)
                return model

        elif ans == 'Default':
            config_automatic = configparser.ConfigParser(allow_no_value=True)
            config_automatic.read('config.ini')
            defaultModelSource = config_automatic['Automatic']['ModelSource']
            return defaultModelSource

    @staticmethod
    def setForceReload():
        """ Choose force reload of pyTorch cache on or off
        :returns: bool """
        ans = pymsgbox.confirm('Reload the pyTorch cache', 
                               'DWLS Setup',
                               buttons = ['Don\'t reload', 'Reload'])

        if ans == 'Reload':
            reloadBoolean = True
        else:
            reloadBoolean = False

        return reloadBoolean


    @staticmethod
    def setCaptureDetection():
        """ Choose if detections should be captured
        :returns: bool """
        ans = pymsgbox.confirm('Save images on detections? Images will be saved at an minimum interval specified by the user.', 
                               'DWLS Setup',
                               buttons = ['Save', 'Don\'t save'])

        if ans == 'Save':
            captureBoolean = True
        else:
            captureBoolean = False

        return captureBoolean

    @staticmethod
    def setCaptureFrequency():
        """ Set the frequency in seconds at interval between detections the application should save a new image
        :returns: int """
        interval = None

        ans = pymsgbox.prompt('Minimum interval in seconds between each picture: ')
        
        try:
            interval = int(ans)
        except Exception:
            pymsgbox.alert('The number must be a valid number [1, 2, ... 59]', 'Error')
            Setup.setCaptureFrequency()
            
        if isinstance(interval, int):
            return interval


    @staticmethod
    def setDetectionThreshold():
        """ Function to set the threshold at which is considered a detection
        :returns: float """
        threshold = None
        ans = pymsgbox.prompt('Input detection confidence threshold (0.0-1.0)')
        
        try:
            threshold = float(ans)
        except Exception:
            pymsgbox.alert('The number must be a valid number [0.0-1.0]', 'Error')
            Setup.setDetectionThreshold()
            
        if isinstance(threshold, float):
            return threshold

    def downloadModel(modelUrl):
        """ Save supplied Model URL to disk
        :returns: str """
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
        response = requests.get(modelUrl, stream=True)
  
        with requests.get(modelUrl, stream=True) as response:
            with open(path_filename, 'wb') as file:
                print('[SETUP] Downloading remote model file ... ')
                shutil.copyfileobj(response.raw, file, )
                    
        print('[SETUP] '+filename+' download complete and saved to '+path)
        return path_filename


    @staticmethod
    def setResolution(): 
        """ Choose the resolution to resize the output image
        :returns: tuple(int, int) """
        ans_width = pymsgbox.prompt('Enter desired screen WIDTH')
        ans_height = pymsgbox.prompt('Enter desired screen HEIGHT')
        
        try:
            width = int(ans_width)
            height = int(ans_height)
        except Exception:
            pymsgbox.alert('The resolution consist of two valid numbers, e.g. 640 by 480')
            Setup.setResolution()
            
        output_dim = width, height
        if isinstance(width, int) and isinstance(height, int):
            return output_dim

    @staticmethod
    def setHeadless():
        """ Choose if detections should be captured
         :returns: bool """
        ans = pymsgbox.confirm('Run in headless mode (without GUI)?', 
                               'DWLS Setup',
                               buttons = ['With GUI', 'Headless'])

        if ans == 'Headless':
            headless_mode = True
        else:
            headless_mode = False

        return headless_mode

    @staticmethod
    def setResize():
        """ Choose if detections should be captured
         :returns: bool """
        ans = pymsgbox.confirm('Resize the image to user-specified dimensions?', 
                               'DWLS Setup',
                               buttons = ['Resize', 'Keep original resolution'])

        if ans == 'Resize':
            resize_flag = True
        else:
            resize_flag = False

        return resize_flag


    def download_newDefaultmodel(modelUrl):
        """ Save supplied Model URL as defaultModel to disk, move the old as RETIRED
        :returns: str """
        path = 'resources/models/'
        defaultModelPath = 'resources/models/defaultModel.pt'
        current_time = time.strftime("%Y-%m-%d_%H-%M-%S", time.gmtime())

        # Move the current defaultModel to RETIRED-time.pt
        old_model_name = f'RETIRED-{current_time}.pt'
        retired_path = os.path.join(path, old_model_name)
        shutil.move(defaultModelPath, retired_path)
        print(f'[SETUP] {defaultModelPath} RETIRED and moved to {retired_path}')

        # Download the file and save to disk as defaultModel.pt
        response = requests.get(modelUrl, stream=True)

        with requests.get(modelUrl, stream=True) as response:
            with open(defaultModelPath, 'wb') as file:
                print('[SETUP] Downloading remote model file ... ')
                shutil.copyfileobj(response.raw, file)
        print('[SETUP] Downloading remote model file ... COMPLETE ')

        return defaultModelPath

