import numpy

# for better IDE Support
if not ('OVBox' in vars() or 'OVBox' in globals()):
    from openvibe import *
if not ('OpenViBE_stimulation' in vars() or 'OpenViBE_stimulation' in globals()):
    from StimulationsCodes import *


class Signal:
    label0 = 0x00008100

    def __init__(self, label_index, frequency):
        self.label = Signal.label0 + label_index
        self.frequency = frequency


def circular_iterator(iterable):
    index = 0
    while True:
        yield iterable[index]
        index = (index + 1) % len(iterable)


class MyOVBox(OVBox):
    def __init__(self):
        OVBox.__init__(self)
        import sys
        print(sys.version)
        self.channelCount = 0
        self.samplingFrequency = 0
        self.epochSampleCount = 0
        self.noiseSigma = 1.
        self.startTime = 0.
        self.endTime = 0.
        self.dimensionSizes = list()
        self.dimensionLabels = list()
        self.timeBuffer = list()
        self.signalBuffer = None
        self.signalHeader = None
        self.signalIterator = None
        self.currentSignal = None
        self.numberOfEpochs = 100
        self.epochCounter = self.numberOfEpochs - 1
        self.experimentLength = 300

    def initialize(self):
        self.channelCount = int(self.setting['Channel count'])
        self.samplingFrequency = int(self.setting['Sampling frequency'])
        self.epochSampleCount = int(self.setting['Generated epoch sample count'])
        self.noiseSigma = self.setting['Noise Normal Distribution Sigma']
        self.experimentLength = float(self.setting['Length in seconds'])
        signals_string = self.setting['Frequencies']
        signals_string = signals_string.split(";")
        signals = []
        for index, frequency in enumerate(signals_string):
            signals.append(Signal(index, float(frequency.strip())))
        self.signalIterator = circular_iterator(signals)
        self.currentSignal = next(self.signalIterator)
        #creation of the signal header
        for i in range(self.channelCount):
            self.dimensionLabels.append('Sinus' + str(i))
        self.dimensionLabels += self.epochSampleCount * ['']
        self.dimensionSizes = [self.channelCount, self.epochSampleCount]
        self.signalHeader = OVSignalHeader(0., 0., self.dimensionSizes, self.dimensionLabels, self.samplingFrequency)
        self.output[0].append(self.signalHeader)
        
        #creation of the first signal chunk
        self.endTime = 1. * self.epochSampleCount / self.samplingFrequency
        self.signalBuffer = numpy.zeros((self.channelCount, self.epochSampleCount))
        self.updateTimeBuffer()
        self.updateSignalBuffer()

        self.output[1].append(OVStimulationHeader(0., 0.))
        
    def updateStartTime(self):
        self.startTime += 1. * self.epochSampleCount / self.samplingFrequency
        
    def updateEndTime(self):
        self.endTime = float(self.startTime + 1. * self.epochSampleCount / self.samplingFrequency)
    
    def updateTimeBuffer(self):
        self.timeBuffer = numpy.arange(self.startTime, self.endTime, 1. / self.samplingFrequency)
        
    def updateSignalBuffer(self):
        frequency = self.currentSignal.frequency
        for rowIndex, row in enumerate(self.signalBuffer):
            self.signalBuffer[rowIndex, :] = 1 * numpy.sin(2. * numpy.pi * frequency * self.timeBuffer)
            self.signalBuffer[rowIndex, :] += numpy.random.normal(0, self.noiseSigma, len(self.timeBuffer))
            
            

    def sendSignalBufferToOpenvibe(self):
        start = self.timeBuffer[0]
        end = self.timeBuffer[-1] + 1. / self.samplingFrequency
        bufferElements = self.signalBuffer.reshape(self.channelCount * self.epochSampleCount).tolist()
        self.output[0].append(OVSignalBuffer(start, end, bufferElements))
    
    def process(self):
        start = self.timeBuffer[0]
        end = self.timeBuffer[-1]

        if self.experimentLength < self.getCurrentTime():
            stimSet = OVStimulationSet(self.experimentLength, self.experimentLength + 1. / self.getClock())
            stimSet.append(OVStimulation(OpenViBE_stimulation['OVTK_StimulationId_ExperimentStop'], self.experimentLength, 0))
            self.output[1].append(stimSet)
            return

        if self.getCurrentTime() >= end:
            self.epochCounter = (self.epochCounter + 1) % self.numberOfEpochs

            if self.epochCounter == 0:
                self.currentSignal = next(self.signalIterator)

                stimSet = OVStimulationSet(self.startTime, self.startTime + 1. / self.getClock())
                stimSet.append(OVStimulation(self.currentSignal.label, self.startTime, self.numberOfEpochs * (self.endTime - self.startTime)))
                self.output[1].append(stimSet)

            self.sendSignalBufferToOpenvibe()
            # the date of the stimulation is simply the current openvibe time when calling the box process
            self.updateStartTime()
            self.updateEndTime()
            self.updateTimeBuffer()
            self.updateSignalBuffer()

    def uninitialize(self):
        end = self.timeBuffer[-1]
        self.output[0].append(OVSignalEnd(end, end))                

box = MyOVBox()
