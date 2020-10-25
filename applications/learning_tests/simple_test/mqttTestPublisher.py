import paho.mqtt.client as mqtt

# This is the publisher
client = mqtt.Client("", True, None, mqtt.MQTTv31)
client.connect("localhost", 1883, 60)
client.publish("topic/test", "Hallo Welt");
client.disconnect();
