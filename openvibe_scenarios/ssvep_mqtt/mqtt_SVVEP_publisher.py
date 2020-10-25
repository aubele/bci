
class MyOVBox(OVBox):
	def __init__(self):

		OVBox.__init__(self)
		self.signalHeader = None #

		self.client = mqtt.Client("", True, None, mqtt.MQTTv31) #
		self.client.connect("localhost", 1883, 60) #

	def initialize(self):
		# nop
		return
		
	def process(self):
		for chunkIndex in range( len(self.input[0]) ):
			chunk = self.input[0].pop()
			if(type(chunk) == OVStimulationSet):
				for stimIdx in range(len(chunk)):
					stim=chunk.pop();
					if stim.identifier == OpenViBE_stimulation["OVTK_StimulationId_Label_00"]:
						self.client.publish("SSVEP", "Oben")
						print 'Oben'
					if stim.identifier == OpenViBE_stimulation["OVTK_StimulationId_Label_01"]:
						self.client.publish("SSVEP", "Links")
						print 'Links'
					if stim.identifier == OpenViBE_stimulation["OVTK_StimulationId_Label_02"]:
						self.client.publish("SSVEP", "Rechts")
						print 'Rechts'
			#else:
			#	print 'Received chunk of type ', type(chunk), " looking for StimulationSet"
		return
		
	def uninitialize(self):
		# nop
		return

box = MyOVBox()
