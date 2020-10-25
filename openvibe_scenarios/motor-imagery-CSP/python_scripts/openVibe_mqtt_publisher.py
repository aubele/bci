import json
import paho.mqtt.client as mqtt

class MyOVBox(OVBox):
    def __init__(self):
        """
        Creates box and connects to MQTT server
        """
        OVBox.__init__(self)
        self.signalHeader = None #

        #Connects to MQTT server
        self.client = mqtt.Client("", True, None, mqtt.MQTTv31) #
        self.client.connect("localhost", 1883, 60) #

        # When using control_Gui.py, set Player = 0
        # When using Ping_Pong.py, set Player = 1 or Player = 2
        self.player = int(self.setting['Player'])

    def process(self):
        """
        Processes the data chunks read in and outputs them--either within
        openVibe or to the MQTT server.
        """
        for chunkIndex in range( len(self.input[0]) ):
            # Header signals the start of the chunk of data in stream
            if(type(self.input[0][chunkIndex]) == OVStreamedMatrixHeader):#
                self.signalHeader = self.input[0].pop()

                # Sets up for outputting data within openVibe
                outputHeader = OVStreamedMatrixHeader( #
                self.signalHeader.startTime,
                self.signalHeader.endTime,
                [1, self.signalHeader.dimensionSizes[1]],
                ['Signal']+self.signalHeader.dimensionSizes[1]*[''])
                #self.signalHeader.samplingRate)

                # Outputs data within openVibe
                #self.output[0].append(outputHeader)

            # The actual data
            elif(type(self.input[0][chunkIndex]) == OVStreamedMatrixBuffer): #
                chunk = self.input[0].pop()
                # Packages info as json and publishes to MQTT server

                if self.player == 0:
                    toPublish = json.dumps(chunk) #For single player
                else:
                    toPublish = json.dumps(self.player, chunk[0], chunk[1]) #For multiplayer
                self.client.publish("topic/bci", toPublish)

                # self.output[0].append(chunk) # Outputs data within openVibe

            # Signals end of the chunk of data in stream
            elif(type(self.input[0][chunkIndex]) == OVSignalEnd):
                # For outputting within openVibe
                #self.output[0].append(self.input[0].pop())
                return 	#unneeded if outputting within openVibe

box = MyOVBox()
