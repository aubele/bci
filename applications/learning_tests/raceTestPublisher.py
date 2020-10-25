import paho.mqtt.client as mqtt
import json

toPublish = json.dumps((2, .3, .7))
# This is the publisher
client = mqtt.Client("", True, None, mqtt.MQTTv31)
client.connect("localhost", 1883, 60)
client.publish("topic/bci", toPublish);
client.disconnect();
