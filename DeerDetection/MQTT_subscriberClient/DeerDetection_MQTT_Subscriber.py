import paho.mqtt.client as mqtt
import time
import json
import jsonschema

from jsonschema import validate

# Init the subscriber
mqttBroker = "mqtt.eclipseprojects.io"
client = mqtt.Client("Subscriber")
client.connect(mqttBroker)

currentTimeStamp = None
currentDetectionCount = None

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

def validateJson(msg):
    """ Function to validate incoming messages against a predefined schema """ 
    try:
        validate(instance=msg, schema=detectionSchema)
        
    except jsonschema.exceptions.ValidationError as err:
        return False
    return True

def on_message(client, userdata, message):
    """ On message recieved do: """
    global currentTimeStamp
    global currentDetectionCount
    jsonToDecode = None
    isValid = False
    

    # Decode the message from an MQTT object to a string
    decodedMessage = message.payload.decode("utf-8")
   
    # Try to check if the json data can be loaded and validated
    try: 
        msg = json.loads(decodedMessage)
        isValid = validateJson(msg)
        
        
    except:
        print(' ... Waiting for data ... ')

    # If the data is valid, get unique timestamp to avoid spam
    if isValid:

        freshTimeStamp = None
        freshDetectionCount = None

        for value in msg:
            freshTimeStamp = msg["time"]
            freshDetectionCount = msg["detectedCount"]

            if (currentTimeStamp != freshTimeStamp) or (currentDetectionCount != freshDetectionCount):
                currentTimeStamp = freshTimeStamp
                currentDetectionCount = freshDetectionCount

                #print(decodedMessage) # Prints JSON-syntax representation of the message
                print(msg) # Prints single line representation of the JSON

            else:
                break



# Run the subscriber loop
client.loop_start()        
print('[MQTT Subscriber] Client running and subscribed to "DEER_DETECTION"')
client.subscribe("DEER_DETECTION")
client.on_message = on_message 
time.sleep(1000)
client.loop_end()               