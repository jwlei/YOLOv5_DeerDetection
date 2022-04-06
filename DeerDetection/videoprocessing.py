import time
import threading
import cv2
import PIL.Image
import pafy # pip install youtube-dl==2020.12.2

import torch
from torch import hub # Hub contains other models like FasterRCNN

class VideoProcessing:
    # -------------------------------------------------- INIT --------------------------------------------------
    def __init__(self, video_source=0, width=None, height=None, fps=None):

        self.video_source = video_source
        self.height = height
        self.width = width
        self.fps = fps

        self.running = False

        # Pre-trained pyTorch model
        model = torch.hub.load( \
                      'ultralytics/yolov5', \
                      'yolov5s', \
                      pretrained=True)


        # Open the video source
        #self.vid = cv2.VideoCapture("http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4")
        # For testing, videocapture(0) = local camera
        # camera_ip = "rtsp://username:password@IP/port"

        URL = "https://www.youtube.com/watch?v=PIN6GaaiNLY" # Video med hjort
        playYt = pafy.new(URL).streams[-1] # -1 = lowest quality

        self.vid = cv2.VideoCapture(playYt.url)
        

        #self.vid = cv2.VideoCapture(video_source) # This pulls from local sources listed in main
       
       
       #found = False
       
       #for i in range(1):
       #    self.vid = cv2.VideoCapture(i)
       #    if not self.vid:
       #        print('[LOG] [ERROR] videoprocessing - VideoProcessing: UNABLE TO CAPTURE MEDIA')
       #    else:
       #        found = True
       #        print('[LOG] videoprocessing - VideoProcessing: CAPTURED MEDIA')
       #        break
       #
       #if found == False:
       #    print('[LOG] [ERROR ]videoprocessing - VideoProcessing: SYS EXIT')
       #    sys.exit()

        

        #cap = cv2.VideoCapture(0)

        #while True:
        #    ret, img = cap.read()
        #    cv2.imshow("Frame", img)
        #    if cv2.waitKey(1) & 0xFF == ord('q'):
        #        break


        print('[LOG] videoprocessing - VideoProcessing - init: cv2.Videocapture ', self.vid)

        # throw error on error
        if not self.vid.isOpened():
            print('[LOG] [ERROR] videoprocessing - VideoProcessing - init: unable to open file', video_source)

        # Get data from video source
        if not self.width:
            self.width = int(self.vid.get(cv2.CAP_PROP_FRAME_WIDTH))    # convert float to int
            print('[LOG] videoprocessing - VideoProcessing - init: IF NOT WIDTH SET TO ', self.width)
        print('[LOG] videoprocessing - VideoProcessing - init: WIDTH SET TO ', self.width)

        if not self.height:
            self.height = int(self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT))  # convert float to int
            print('[LOG] videoprocessing - VideoProcessing - init: IF NOT HEIGHT SET TO ', self.height)
        print('[LOG] videoprocessing - VideoProcessing - init: HEIGHT SET TO ', self.height)

        if not self.fps:
            self.fps = int(self.vid.get(cv2.CAP_PROP_FPS))              # convert float to int
            print('[LOG] videoprocessing - VideoProcessing - init: FPS SET TO ', self.fps)

        # Set default values
        self.ret = False
        self.frame = None
        self.convert_color = cv2.COLOR_BGR2RGB
        self.convert_pillow = True

        # default values for recording
        self.recording = False
        self.recording_filename = 'output.avi'
        self.recording_writer = None

        # Start a thread
        self.running = True
        self.thread = threading.Thread(target=self.process)
        #self.thread = threading.Thread(target=self.pyTorch)
        self.thread.start()


    # -------------------------------------------------- SNAPSHOT --------------------------------------------------    
    def snapshot(self, filename=None):

        if not self.ret:
            print('[LOG][ERROR] videoprocessing - VideoProcessing - snapshot:  no frame for snapshot')
        else:
            if not filename:
                filename = time.strftime("Snapshot %d-%m-%Y_%H-%M-%S.jpg")

            if not self.convert_pillow:
                cv2.imwrite(filename, self.frame)
                print('[LOG] videoprocessing - VideoProcessing - snapshot: saved (using cv2):', filename)
            else:
                self.frame.save(filename)
                print('[LOG] videoprocessing - VideoProcessing - snapshot: saved (using pillow):', filename)


    # -------------------------------------------------- PROCESS --------------------------------------------------
    def process(self):

        while self.running:
            ret, frame = self.vid.read()
            # TODO: Call pytorch on the videostream, fix output from pytorch so that we see boxes
            # self.pyTorch()

            if ret:
                # process image
                frame = cv2.resize(frame, (self.width, self.height))

                if self.convert_pillow:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame = PIL.Image.fromarray(frame)
                    
            
            else:
                print('[LOG] videoprocessing - process: stream end:', self.video_source)
                # TODO: Fix re-run/re-open of inputData
                self.running = False
                break

            # assign new frame
            # returns true if the frame is available
            self.ret = ret
            # the array vector captured based on the default frames per second defined
            self.frame = frame
            print('[LOG] videoprocessing - process: new frame ', self.ret, self.frame)

            # sleep for next frame
            #time.sleep(1/self.fps)
            # TODO: Fix fps read
            time.sleep(1/30)
            # REDUCE SPAM print('[LOG] videoprocessing - process: thread sleeping for 1/30')

    # -------------------------------------------------- GET FRAME --------------------------------------------------
    def get_frame(self):
        return self.ret, self.frame
        print('[LOG] videoprocessing - get_frame: ', self.ret, self.frame)


    def __del__(self):
        """TODO: add docstring"""

        # stop thread
        if self.running:
            self.running = False
            self.thread.join()

        # relase stream
        if self.vid.isOpened():
            self.vid.release()



    # -------------------------------------------------- PyTorch stuff --------------------------------------------------

    """
    The function below identifies the device which is availabe to make the prediction and uses it to load and infer the frame. Once it has results it will extract the labels and cordinates(Along with scores) for each object detected in the frame.
    """
    def score_frame(frame, model):
        #device = 'cuda' if torch.cuda.is_available() else 'cpu'
        device = 'cpu'
        model.to(device)
        frame = [torch.tensor(frame)]
        results = self.model(frame)
        labels = results.xyxyn[0][:, -1].numpy()
        cord = results.xyxyn[0][:, :-1].numpy()
        print('[LOG] videoprocessing - score_frame: FRAME SCORED')
        return labels, cord


    """
    The function below takes the results and the frame as input and plots boxes over all the objects which have a score higer than our threshold.
    """
    def plot_boxes(self, results, frame):
        labels, cord = results
        n = len(labels)
        x_shape, y_shape = frame.shape[1], frame.shape[0]
        for i in range(n):
            row = cord[i]
            # If score is less than 0.2 we avoid making a prediction.
            if row[4] < 0.2: 
                continue
            x1 = int(row[0]*x_shape)
            y1 = int(row[1]*y_shape)
            x2 = int(row[2]*x_shape)
            y2 = int(row[3]*y_shape)
            bgr = (0, 255, 0) # color of the box
            classes = self.model.names # Get the name of label index
            label_font = cv2.FONT_HERSHEY_SIMPLEX #Font for the label.
            cv2.rectangle(frame, \
                          (x1, y1), (x2, y2), \
                           bgr, 2) #Plot the boxes
            cv2.putText(frame,\
                        classes[labels[i]], \
                        (x1, y1), \
                        label_font, 0.9, bgr, 2) #Put a label over box.
            print('[LOG] videoprocessing - plot_boxes: APPLIED')
            return frame


    """
    The Function below oracestrates the entire operation and performs the real-time parsing for video stream.
    """
    def pyTorch(self):
        self.recording == True
        #player = self.vid #Get your video stream.
        assert self.vid.isOpened() # Make sure that their is a stream. 
        #Below code creates a new video writer object to write our
        #output stream.
        x_shape = int(self.vid.get(cv2.CAP_PROP_FRAME_WIDTH))
        y_shape = int(self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
        four_cc = cv2.VideoWriter_fourcc(*"MP42") #Using MJPEG codex
        out = cv2.VideoWriter(self.recording_filename, four_cc, 20, \
                              (x_shape, y_shape)) 
        ret, frame = self.vid.read() # Read the first frame.

        while self.recording: # Run until stream is out of frames
            print('[LOG] videoprocessing - pyTorch: IS RECORDING')
            start_time = time() # We would like to measure the FPS.
            results = self.score_frame(frame) # Score the Frame
            frame = self.plot_boxes(results, frame) # Plot the boxes.
            end_time = time()
            fps = 1/np.round(end_time - start_time, 3) #Measure the FPS.
            print(f"Frames Per Second : {fps}")
            out.write(frame) # Write the frame onto the output.
            ret, frame = self.vid.read() # Read next frame.