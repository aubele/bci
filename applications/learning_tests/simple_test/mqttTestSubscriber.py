import paho.mqtt.client as mqtt


# This is the subscriber

def on_connect(client, userdata, flags, rc):
    print("Connected with result code" + str(rc))
    client.subscribe("topic/testing")


def on_message(client, userdata, msg):
    if (msg.payload == "Hallo Welt"):
        print("Yes!")
        client.disconnect()
    else:
	print(msg.payload)


client = mqtt.Client("", True, None, mqtt.MQTTv31)
client.connect("localhost", 1883, 60)

client.on_connect = on_connect
client.on_message = on_message

client.loop_forever()
