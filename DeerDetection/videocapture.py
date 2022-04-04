import time
import threading
import cv2
import PIL.Image

class VideoCapture:


    # -------------------------------------------------- INIT --------------------------------------------------
    def __init__(self, video_source=0, width=None, height=None, fps=None):

        self.video_source = video_source
        self.width = width
        self.height = height
        self.fps = fps

        self.running = False

        # Open the video source
        self.vid = cv2.VideoCapture(video_source)
        if not self.vid.isOpened():
            raise ValueError("[ERROR] Unable to open video source", video_source)

        # Get video source width and height
        if not self.width:
            self.width = int(self.vid.get(cv2.CAP_PROP_FRAME_WIDTH))    # convert float to int
        if not self.height:
            self.height = int(self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT))  # convert float to int
        if not self.fps:
            self.fps = int(self.vid.get(cv2.CAP_PROP_FPS))              # convert float to int

        # default value at start
        self.ret = False
        self.frame = None

        self.convert_color = cv2.COLOR_BGR2RGB
        #self.convert_color = cv2.COLOR_BGR2GRAY
        self.convert_pillow = True

        # default values for recording
        self.recording = False
        self.recording_filename = 'output.mp4'
        self.recording_writer = None

        # start thread
        self.running = True
        self.thread = threading.Thread(target=self.process)
        self.thread.start()


    # -------------------------------------------------- SNAPSHOT --------------------------------------------------    
    def snapshot(self, filename=None):

        if not self.ret:
            print('[ERROR] no frame for snapshot')
        else:
            if not filename:
                filename = time.strftime("Snapshot %d-%m-%Y_%H-%M-%S.jpg")

            if not self.convert_pillow:
                cv2.imwrite(filename, self.frame)
                print('[LOG] snapshot (using cv2):', filename)
            else:
                self.frame.save(filename)
                print('[LOG] snapshot (using pillow):', filename)

    # -------------------------------------------------- PROCESS --------------------------------------------------
    def process(self):

        while self.running:
            ret, frame = self.vid.read()

            if ret:
                # process image
                frame = cv2.resize(frame, (self.width, self.height))

                # it has to record before converting colors
                if self.recording:
                    self.record(frame)

                if self.convert_pillow:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame = PIL.Image.fromarray(frame)
            else:
                print('[LOG] stream end:', self.video_source)
                # TODO: reopen stream
                self.running = False
                if self.recording:
                    self.stop_recording()
                break

            # assign new frame
            self.ret = ret
            self.frame = frame

            # sleep for next frame
            #time.sleep(1/self.fps)
            time.sleep(1/30)

    def get_frame(self):
        return self.ret, self.frame

    # Release the video source when the object is destroyed
    def __del__(self):

        # stop thread
        if self.running:
            self.running = False
            self.thread.join()

        # relase stream
        if self.vid.isOpened():
            self.vid.release()