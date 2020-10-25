import numpy as np
from sklearn.externals import joblib
from sklearn.metrics import confusion_matrix, classification_report

if not ('OVBox' in vars() or 'OVBox' in globals()):
    from openvibe import *

class MyOVBox(OVBox):
    def __init__(self):
        OVBox.__init__(self)

        self.currentStimulationTarget = 0
        self.currentStimulationTargetTime = self.getCurrentTime()
        self.currentStimulationEndTime = None

        self.data = []
        self.targets = []
        self.signalHeader = None

    def initialize(self):
        self.clf = joblib.load(self.setting["output"] + "/clf.pkl")

    def process(self):
        #signals

        signalInput = self.input[0]
        for chunkIndex in range(len(signalInput)): 
            if type(signalInput[chunkIndex]) == OVSignalHeader:
                signalHeader = signalInput.pop()
                self.signalHeader = signalHeader
                
            elif type(signalInput[chunkIndex])  == OVSignalBuffer:
                chunk = signalInput.pop()

                numpyBuffer = np.array(chunk, dtype=np.float64).reshape(tuple(self.signalHeader.dimensionSizes))
                preprocessedData = self.preprocess_data(numpyBuffer)
                
                self.data.append(preprocessedData)
                self.targets.append(self.currentStimulationTarget)

                if self.getCurrentTime() > self.currentStimulationEndTime:
                    self.currentStimulationTarget = 0

            elif type(signalInput[chunkIndex]) == OVSignalEnd:
                    pass
        

        #stims

        stimInput = self.input[1]
        for chunkIdx in range(len(stimInput)):
            chunk = stimInput.pop()
            if type(chunk) == OVStimulationSet:
                for stimIdx in range(len(chunk)):
                    stim = chunk.pop()
                    if stim.identifier == OpenViBE_stimulation['OVTK_StimulationId_ExperimentStop']:
                        self.start_test()
                    else:
                        self.currentStimulationTargetTime = self.getCurrentTime()
                        self.currentStimulationEndTime = self.getCurrentTime() + float(stim.duration)
                        self.currentStimulationTarget = stim.identifier - OpenViBE_stimulation['OVTK_StimulationId_Label_00']

        if self.getCurrentTime() > self.currentStimulationEndTime:
            self.currentStimulationTarget = 0

    def uninitialize(self):
        return

    def start_test(self):
        self.data = np.array(self.data)
        nsamples, nx, ny = self.data.shape
        self.data = self.data.reshape((nsamples,nx*ny))

        X_test = np.array(self.data, dtype=np.float32).reshape((-1, nx, ny))
        y_test = np.array(self.targets, dtype=np.int32)

        print("Starting classificator test with " + str(y_test.size) + " samples.")
        accuracy = self.clf.score(X_test, y_test)
        
        y_pred = self.clf.predict(X_test)
        cm = confusion_matrix(y_test, y_pred)
        target_names = ['class 0', 'class 1', 'class 2', 'class 3']
        print(classification_report(y_test, y_pred, target_names=target_names))
        print("Got accuracy of " + str(accuracy) + "\n") 
        print("Confusion Matrix:")
        print(cm)

        self.send_stop_stim()

    
    def preprocess_data(self, datachunk):
        datachunk = np.abs(np.fft.rfft(datachunk))
        return datachunk

    def send_stop_stim(self):
        stimSet = OVStimulationSet(self.getCurrentTime(), self.getCurrentTime()+1./self.getClock()) 
        stimSet.append(OVStimulation(OpenViBE_stimulation['OVTK_StimulationId_Label_00'], self.getCurrentTime(), 0.))
        self.output[0].append(stimSet)

box = MyOVBox()
