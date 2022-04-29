import json
import paho.mqtt.client as mqtt

import jsonschema
from jsonschema import validate

newSource = None


class Mqtt_subscriber:
    """ MQTT Subscriber class """
    def __init__(self):
        """ Initialization of class """
        self.mqttBroker = "mqtt.eclipseprojects.io"
        self.topic = "DEER_DETECTION_REFRESH"
        self.client = mqtt.Client("remote_device")
        self.client.connect(self.mqttBroker)
        print(f'[MQTT INTERNAL SUBSCRIBER] Initializing.. ')

    def validateJson(msg):
        """ Function to validate incoming messages against a predefined schema """
        # Validation schema
        validationSchema_Msg = {
            "type": "object",
            "properties": {
                "newSource": {"type": "string"}
            },
        }

        try:
            validate(instance=msg, schema=validationSchema)
        except jsonschema.exceptions.ValidationError as err:
            return False
        return True


    def on_message(self, client, userdata, message):
        """ On message recieved do: """
        global newSource

        isValid = False
        decodedMessage = message.payload.decode("utf-8")                            # Decode the message from an MQTT object to a string
        print(decodedMessage)
        print(isValid)
        try:                                                                        # Try to check if the json data can be loaded and validated
            msg = json.loads(decodedMessage)
            isValid = validateJson(msg)
        except:
            print('[MQTT Subscriber] Recieved msg not valid JSON schema')
            pass
        isValid = True

        if isValid and msg["newSource"] is not None:                                                                 # If the data is valid, get unique timestamp to avoid spam from the publisher
            newSource = msg["newSource"]
            print('--------------------------------------------------------')
            print(f'[MQTT INTERNAL SUBSCRIBER] NEW MODEL SOURCE INCOMING')
            print(f'{msg["newSource"]}')
            print('--------------------------------------------------------')
        else:
            print('--------------------------------------------------------')
            print(f'[MQTT INTERNAL SUBSCRIBER] ATTEMPTED PUSH OF NEW SOURCE')
            print(f'[MQTT INTERNAL SUBSCRIBER] BUT MESSAGE WAS INVALID')
            print('--------------------------------------------------------')
            pass

        
    def get_mqtt_source(self):
        """ Return the newSource recieved from a message """
        global newSource
        return newSource

    def reset_mqtt_source(self):
        """ Reset the variable """
        global newSource
        newSource = None

# ------------------------------ Run the client ------------------------------ #
    def launch(self):
        """ Start the client loop """
        self.client.loop_start()
        self.client.subscribe(self.topic)
        print(f'[MQTT INTERNAL SUBSCRIBER] launched and subscribing to {self.topic}')
        self.client.on_message = self.on_message

