import paho.mqtt.client as mqtt
import json
import time
import sys

class Mqtt_publisher:
    """ Class which contains functionality of an MQTT Message publisher """ 

    def __init__(self):
        """ Initialize the client with settings like: """
        self.mqttBroker = "mqtt.eclipseprojects.io"
        self.client = mqtt.Client("DWLS_REFRESH_MODEL")
        self.client.connect(self.mqttBroker)
        print('[MQTT EXTERNAL PUBLISHER] Client initialized')




    def publishNewSource(self, new_source):
        """ Publish a default message containing no specific string Message """
        msg = json.dumps({'newSource' : new_source
                        }, indent = 4)

        self.client.publish("DWLS_REFRESH", msg)
        print(f'[MQTT EXTERNAL PUBLISHER] has sendt {msg} to all subscribers')

if __name__ == "__main__":
    new_source = str(sys.argv[1])

# to run python ext_MQTT_Publisher.py https://dl.dropboxusercontent.com/s/5p2onyp5m7apxrj/best.pt
#new_source = 'https://dl.dropboxusercontent.com/s/5p2onyp5m7apxrj/best.pt'
pub = Mqtt_publisher()
pub.publishNewSource(new_source)