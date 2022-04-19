import paho.mqtt.client as mqtt
import time

def on_message(client, userdata, message):
    print("Received message: ", str(message.payload.decode("utf-8")))

mqttBroker = "mqtt.eclipseprojects.io"
client = mqtt.Client("Subscriber")
client.connect(mqttBroker)

client.loop_start()
print('Client running and subscribed to "DEER_DETECTION_LOG"')
client.subscribe("DEER_DETECTION_LOG")
client.on_message = on_message
time.sleep(1000)
client.loop_end()