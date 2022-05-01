import paho.mqtt.client as mqtt
import time
import json
import jsonschema
import logging
import tkinter as tk

from tkinter import font as tkFont
from jsonschema import validate

# Global variables
currentTimeStamp = None
currentDetectionCount = None
lastDetectedTimeStamp = None

class MQTT_Subscriber:
    """ MQTT Subscriber client class """
    def __init__(self):
        """ Function to which is called on initialization """
        # GUI
        self.alarmWindow = tk.Tk()
        self.alarmWindow.title("EXTERNAL MQTT Subscriber: I'm getting a remote warning")
        self.alarmWindow.geometry("500x250")

        self.helvetica = tkFont.Font(family="Helvetica", size=16)
        self.alert_status = tk.Label(text='Waiting for input',
                                     bg='orange',
                                     font = self.helvetica)
        self.alert_status.pack(fill="both", expand=True)

        self.alert_Timestamp = tk.Label(bg='orange',
                                        font = self.helvetica,
                                        wraplength = 400)
        self.alert_Timestamp.pack(fill="both", expand=True)


        # Logging
        self.file_log_detections = "external_mqtt_logs/log_detections.txt"
        self.file_log_mqtt = "external_mqtt_logs/log_mqtt.log"

        # Logging basic config for MQTT
        logging.basicConfig(filename = self.file_log_mqtt,  # Log to fresh file
                            filemode = 'w',                 # every launch
                            encoding = 'utf-8',
                            format = '%(message)s')

        self.console = logging.StreamHandler()
        self.console.setLevel(logging.INFO)
        self.logger = logging.getLogger('').addHandler(self.console)

        logging.warning('[MQTT EXTERNAL SUBSCRIBER] Initializing')
        logging.warning(f'[MQTT EXTERNAL SUBSCRIBER] MQTT Subscriber log can be found at {self.file_log_mqtt}')

        # Just getting a fresh file to write detections in
        self.log_detections = open(self.file_log_detections, "w") # "a" if we rather want to append
        self.log_detections.write('')
        self.log_detections.close()


        # MQTT Subscriber client
        self.mqttBroker = "mqtt.eclipseprojects.io"
        self.topic = "DWLS_DETECTION"
        self.client = mqtt.Client("EXTERNAL_SUBSCRIBER")
        self.client.connect(self.mqttBroker)

    def validateJson(self, msg):
        """ Function to validate incoming messages against a predefined schema
        :param str msg: A string message in a JSON format
        :return: bool
        """
        # Validation schemas
        validationSchema_Msg = {
            "type": "object",
            "properties": {
                "msg": {"type": "string"},
                "time": {"type": "string"},
                "location": {"type": "string"},
                "detected": {"type": "boolean"},
                "detectedCount": {"type": "number"},
                "lowestConfidence": {"type": ["number", "null"]},
                "highestConfidence": {"type": ["number", "null"]}
            },
        }

        validationSchema_noMsg = {
            "type": "object",
            "properties": {
                "time": {"type": "string"},
                "location": {"type": "string"},
                "detected": {"type": "boolean"},
                "detectedCount": {"type": "number"},
                "lowestConfidence": {"type": ["number", "null"]},
                "highestConfidence": {"type": ["number", "null"]}
            },
        }


        try:
            validate(instance=msg, schema=validationSchema_noMsg)

        except jsonschema.exceptions.ValidationError as err:
            try:
                validate(instance=msg, schema=validationSchema_Msg)
            except jsonschema.exceptions.ValidationError as err:
                return False
        return True


    def on_message(self, client, userdata, message):
        """ On message received, print the message and change the GUI Detection status
        :param str message: An encoded message received from a MQTT Publisher
        """
        global currentTimeStamp
        global currentDetectionCount
        global lastDetectedTimeStamp
        isValid = False
        self.log_detections = open(self.file_log_detections, "a")    # "a" add to file, "w" overwrite
        decodedMessage = message.payload.decode("utf-8")             # Decode the message from an MQTT object to a string

        try:        # Try to check if the json data can be loaded and validated
            msg = json.loads(decodedMessage)
            isValid = self.validateJson(msg)
        except:
            print('[MQTT EXTERNAL SUBSCRIBER] Recieved message does not match JSON schema or is empty')
            pass

        if isValid: # If the data is valid, get unique timestamp to avoid spam from the publisher
            freshTimeStamp = None
            freshDetectionCount = None

            for value in msg:
                freshTimeStamp = msg["time"]
                freshDetectionCount = msg["detectedCount"]

                # Only log/print if there is a difference in detection and a second has passed
                if (currentTimeStamp != freshTimeStamp) or (currentDetectionCount != freshDetectionCount) and freshDetectionCount != 0:
                    currentTimeStamp = freshTimeStamp
                    currentDetectionCount = freshDetectionCount

                    if msg["detected"]:
                        self.alert_status.config(bg="red", text="DETECTED")
                        self.alert_Timestamp.config(bg="red", text=f'{freshTimeStamp}')
                        lastDetectedTimeStamp = freshTimeStamp

                        self.log_detections.write(str(msg)) # Write to detections log file
                        self.log_detections.write('\n')

                    elif "msg" in msg:
                        no_input = msg["msg"]
                        timestamp = msg["time"]
                        print(f'[MQTT EXTERNAL SUBSCRIBER] {no_input} at {timestamp}')


                    else:
                        self.alert_status.config(bg="green", text="NO DETECTION")
                        self.alert_Timestamp.config(bg="green")
                        if lastDetectedTimeStamp is not None:
                            self.alert_Timestamp.config(bg="green", text = f'Last detection occured at {lastDetectedTimeStamp}')

                    #print(decodedMessage)                          # Prints JSON-syntax representation of the message
                    print(f'[MQTT EXTERNAL SUBSCRIBER] {msg}')      # Prints single line representation of the JSON

                else:
                    break

            self.log_detections.close()


    def launch(self):
        """ Function to launch the External MQTT Subscriber client """
        self.client.loop_start()
        logging.warning('[MQTT EXTERNAL SUBSCRIBER] Client loop started')
        self.client.subscribe(self.topic)
        logging.warning(f'[MQTT EXTERNAL SUBSCRIBER] Subscribed to: {self.topic}')
        self.client.on_message = self.on_message
        logging.warning(f'[MQTT EXTERNAL SUBSCRIBER] Setup complete, detections are logged to {self.file_log_detections}')

        self.alarmWindow.mainloop()


mqtt_client = MQTT_Subscriber()
mqtt_client.launch()
