import paho.mqtt.client as mqtt
import json
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
        """ Publish a default message containing no specific string Message
         :param str new_source: Incoming URL for source
        """
        msg = json.dumps({'newSource' : new_source
                        }, indent = 4)

        self.client.publish("DWLS_REFRESH_MODEL", msg)
        print(f'[MQTT EXTERNAL PUBLISHER] has sendt {msg} to all subscribers')

if __name__ == "__main__":
    try:
        new_source = str(sys.argv[1])
    except Exception:
        new_source = 'EMPTY'



# to run python ext_MQTT_Publisher.py https://dl.dropboxusercontent.com/s/5p2onyp5m7apxrj/best.pt
#new_source = 'https://dl.dropboxusercontent.com/s/5p2onyp5m7apxrj/best.pt'
pub = Mqtt_publisher()
if new_source == 'EMPTY':
    print('[ERROR] URL must be supplied with the command')
    print('[ERROR] E.g. python ext_mqtt_publisher.py https://your.url/modelFile.pt')
else:
    pub.publishNewSource(new_source)

