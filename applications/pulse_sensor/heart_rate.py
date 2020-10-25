#!/bin/env python

"""
Read A0 from PCF8591 and print it to console
"""

import smbus
import time
import csv
from collections import deque
import paho.mqtt.client as mqtt


mqtt_client = mqtt.Client("", True, None, mqtt.MQTTv31)
mqtt_client.connect("10.42.0.1")

bus = smbus.SMBus(1)
i2c_addr = 0x48
chip_addr = 0x40

sleeptime = 0.01
time_last = 0

prev_readouts = deque([0, 0], maxlen=2)
reject_low = 40
reject_high = 200
threshold = 240

rate_buffer = deque([], maxlen=10)

out_file = open("pulse.csv", mode="w+")
#csv_writer = csv.writer(out_file)
#csv_writer.writerow(["Time Elapsed", "Pulse Measurement"])


while True:
    bus.read_byte_data(i2c_addr, chip_addr)
    readout = bus.read_byte_data(i2c_addr, chip_addr)
    # if readoud rises above threshold
    if prev_readouts[-1] < threshold and readout > threshold:
        now = time.time()
        # calculate the theoritical rate from the time between now an the previous heartbeat
        current_rate = 60. / (now - time_last)
       
        if current_rate < reject_high:
            time_last = now
            if current_rate > reject_low:
                rate_buffer.append(current_rate)
                mqtt_client.publish("heart_rate", sum(rate_buffer) / float(len(rate_buffer)))
                print(sum(rate_buffer) / float(len(rate_buffer)))
 
    prev_readouts.append(readout)
    time.sleep(0.01)
