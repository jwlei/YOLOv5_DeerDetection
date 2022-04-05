import time
import threading
import cv2
import PIL.Image

class VideoProcessing:
    # -------------------------------------------------- INIT --------------------------------------------------
    def __init__(self, video_source=0, width=None, height=None, fps=None):

        self.video_source = video_source
        self.width = width
        self.height = height
        self.fps = fps

        self.running = False

        # Open the video source
        self.vid = cv2.VideoCapture(video_source)

        # throw error on error
        if not self.vid.isOpened():
            print('[LOG][ERROR] unable to open file', video_source)

        # Get data from video source
        if not self.width:
            
            self.width = int(self.vid.get(cv2.CAP_PROP_FRAME_WIDTH))    # convert float to int
            print('[LOG] WIDTH SET TO ', self.width)
        if not self.height:
            self.height = int(self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT))  # convert float to int
            print('[LOG] HEIGHT SET TO ', self.height)
        if not self.fps:
            self.fps = int(self.vid.get(cv2.CAP_PROP_FPS))              # convert float to int
            print('[LOG] FPS SET TO ', self.fps)

        # Set default values
        self.ret = False
        self.frame = None
        self.convert_color = cv2.COLOR_BGR2RGB
        self.convert_pillow = True

        # Start a thread
        self.running = True
        self.thread = threading.Thread(target=self.process)
        self.thread.start()


    # -------------------------------------------------- SNAPSHOT --------------------------------------------------    
    def snapshot(self, filename=None):

        if not self.ret:
            print('[LOG][ERROR] no frame for snapshot')
        else:
            if not filename:
                filename = time.strftime("Snapshot %d-%m-%Y_%H-%M-%S.jpg")

            if not self.convert_pillow:
                cv2.imwrite(filename, self.frame)
                print('[LOG] snapshot saved (using cv2):', filename)
            else:
                self.frame.save(filename)
                print('[LOG] snapshot saved (using pillow):', filename)


    # -------------------------------------------------- PROCESS --------------------------------------------------
    def process(self):

        while self.running:
            ret, frame = self.vid.read()

            if ret:
                # process image
                frame = cv2.resize(frame, (self.width, self.height))

                if self.convert_pillow:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame = PIL.Image.fromarray(frame)
            else:
                print('[LOG] stream end:', self.video_source)
                """ TODO: Fix re-run/re-open of inputData """
                self.running = False
                break

            # assign new frame
            self.ret = ret
            self.frame = frame
            print('[LOG] VideoProcessing - process - new frame ', self.ret, self.frame)

            # sleep for next frame
            #time.sleep(1/self.fps)
            """ TODO: Fix fps """
            time.sleep(1/30)
            print('[LOG] VideoProcessing - process thread sleeing for 1/30')

    # -------------------------------------------------- GET FRAME --------------------------------------------------
    def get_frame(self):
        return self.ret, self.frame
