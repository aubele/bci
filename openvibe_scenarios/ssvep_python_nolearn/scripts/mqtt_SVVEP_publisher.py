import json
import paho.mqtt.client as mqtt

if not ('OVBox' in vars() or 'OVBox' in globals()):
    from openvibe import *

class MyOVBox(OVBox):
    """
    This Python Script for the OVBox establishes a connection to the MQTT Host
    on 10.0.2.2(the Host System for the VM) and takes the Stimulations from
    OpenVibe interprets them and publishes the corresponding Message over MQTT
    """
    def __init__(self):

        OVBox.__init__(self)
        #establishes the connection
        self.signalHeader = None #
        self.client = mqtt.Client("", True, None, mqtt.MQTTv31) #
        self.client.connect("localhost")
        self.identifierHitDict = {
            OpenViBE_stimulation["OVTK_StimulationId_Label_01"]: [],
            OpenViBE_stimulation["OVTK_StimulationId_Label_02"]: [],
            OpenViBE_stimulation["OVTK_StimulationId_Label_03"]: [],
        }
        self.directionMap = {
            OpenViBE_stimulation["OVTK_StimulationId_Label_01"]: 1,
            OpenViBE_stimulation["OVTK_StimulationId_Label_02"]: 2,
            OpenViBE_stimulation["OVTK_StimulationId_Label_03"]: 3,
        }

        self.timeframe = 2000
        self.necessaryHits = 4
        self.last_send = self.getCurrentTime()

    def initialize(self):
        # nop
        return

    def process(self):
        for chunkIndex in range( len(self.input[0]) ):
            chunk = self.input[0].pop()
            if(type(chunk) == OVStimulationSet):
                for stimIdx in range(len(chunk)):
                    stim=chunk.pop()
                    timestamp = self.getCurrentTime() * 1000
                    if (stim.identifier == OpenViBE_stimulation['OVTK_StimulationId_Label_00']): continue
                    self.identifierHitDict[stim.identifier].append(timestamp)

                    if len(filter(lambda x: timestamp - self.timeframe < x < timestamp, self.identifierHitDict[stim.identifier])) >= self.necessaryHits \
                    and (timestamp / 1000) - self.last_send > 0.1:
                        self.last_send = self.getCurrentTime()
                        print("sending " + str(self.directionMap[stim.identifier]))
                        self.client.publish("SSVEP", self.directionMap[stim.identifier])
                        self.identifierHitDict[stim.identifier] = filter(lambda x: x > timestamp - self.timeframe, self.identifierHitDict[stim.identifier])

        return

    def uninitialize(self):
        # nop
        return

box = MyOVBox()
