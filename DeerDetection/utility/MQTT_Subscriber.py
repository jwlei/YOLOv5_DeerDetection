import paho.mqtt.client as mqtt
import time
import json
import jsonschema
import logging
import tkinter as tk

from tkinter import font as tkFont
from jsonschema import validate

""" MQTT Subscriber class """ 
# ------------------------------ GUI ------------------------------ #
alarmWindow = tk.Tk()
alarmWindow.title("MQTT Subscriber: I'm getting a remote warning")
alarmWindow.geometry("450x250")

helvetica = tkFont.Font(family="Helvetica", size=16)
alert_status = tk.Label(text='Waiting for input', 
                        bg='orange', 
                        font = helvetica)
alert_status.pack(fill="both", expand=True)

alert_Timestamp = tk.Label(bg='orange', 
                           font = helvetica, 
                           wraplength = 400)
alert_Timestamp.pack(fill="both", expand=True)


# ------------------------------ Logging ------------------------------ #
file_log_detections = "docs/log_detections.txt"
file_log_mqtt = "docs/log_mqtt.log"

# Logging basic config for MQTT 
logging.basicConfig(filename = file_log_mqtt, # Log to fresh file
                    filemode = 'w',           # every launch
                    encoding = 'utf-8', 
                    format = '%(message)s')

console = logging.StreamHandler()
console.setLevel(logging.INFO)
logger = logging.getLogger('').addHandler(console)

logging.warning('[MQTT Subscriber] Initializing')
logging.warning(f'[MQTT Subscriber] MQTT Subscriber log can be found at {file_log_mqtt}')

# Just getting a fresh file to write detections in
# TODO: New log file on each run (?)
log_detections = open(file_log_detections, "w") # "a" if we rather want to append
log_detections.write('')
log_detections.close()

# ------------------------------ MQTT Subscriber client ------------------------------ #
mqttBroker = "mqtt.eclipseprojects.io"
topic = "DEER_DETECTION"
client = mqtt.Client("Subscriber")
client.connect(mqttBroker)

currentTimeStamp = None
currentDetectionCount = None
lastDetectedTimeStamp = None



# ------------------------------ Logic ------------------------------ #

def validateJson(msg):
    """ Function to validate incoming messages against a predefined schema """
    # Validation schema
    detectionSchema = {
            "type": "object",
            "properties": {
                "time": {"type": "string"},
                "location": {"type": "string"},
                "detected": {"type": "boolean"},
                "detectedCount": {"type": "number"},
            },
    }

    try:
        validate(instance=msg, schema=detectionSchema) 
    except jsonschema.exceptions.ValidationError as err:
        return False
    return True

def on_message(client, userdata, message):
    """ On message recieved do: """
    global currentTimeStamp
    global currentDetectionCount
    global lastDetectedTimeStamp
    jsonToDecode = None
    isValid = False

    log_detections = open(file_log_detections, "a") # "a" add to file, "w" overwrite

    # Decode the message from an MQTT object to a string
    decodedMessage = message.payload.decode("utf-8")
   
    # Try to check if the json data can be loaded and validated
    try: 
        msg = json.loads(decodedMessage)
        isValid = validateJson(msg) 
    except:
        pass

    # If the data is valid, get unique timestamp to avoid spam
    if isValid:

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
                    alert_status.config(bg="red", text="DETECTED")
                    alert_Timestamp.config(bg="red", text=f'{freshTimeStamp}')
                    lastDetectedTimeStamp = freshTimeStamp

                else:
                    alert_status.config(bg="green", text="NO DETECTION")
                    alert_Timestamp.config(bg="green")
                    if lastDetectedTimeStamp is not None:
                        alert_Timestamp.config(bg="green", text = f'Last detection occured at {lastDetectedTimeStamp}')
                    
                #print(decodedMessage) # Prints JSON-syntax representation of the message
                print(msg) # Prints single line representation of the JSON
                log_detections.write(str(msg)) # Write to detections log file
                log_detections.write('\n')
            else:
                
                break
        log_detections.close()
                

# ------------------------------ Run the client ------------------------------ #

client.loop_start() 
logging.warning('[MQTT Subscriber] Client loop started')
client.subscribe(topic)
logging.warning(f'[MQTT Subscriber] Subscribed to: {topic}')

client.on_message = on_message

alarmWindow.mainloop()
logging.warning(f'[MQTT Subscriber] Setup complete, detections are logged to {file_log_detections}')

#Timeout
time.sleep(100000)
client.loop_end() 