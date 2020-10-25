import numpy as np
from sklearn.externals import joblib
from sklearn.metrics import confusion_matrix, classification_report

if not ('OVBox' in vars() or 'OVBox' in globals()):
    from openvibe import *

class MyOVBox(OVBox):
    def __init__(self):
        OVBox.__init__(self)

        self.data = []
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

                numpyBuffer = np.array(chunk, dtype=np.float32).reshape(tuple(self.signalHeader.dimensionSizes))

                preprocessedData = self.preprocess_data(numpyBuffer)
                nx, ny = preprocessedData.shape
                preprocessedData = preprocessedData.reshape(1, nx, ny)
                
                
                self.predict(preprocessedData)

            elif type(signalInput[chunkIndex]) == OVSignalEnd:
                    pass
        

    def uninitialize(self):
        return

    def predict(self, data):
        prediction = self.clf.predict(data.astype(np.float32))

        stimSet = OVStimulationSet(self.getCurrentTime(), self.getCurrentTime()+1./self.getClock()) 
        stimSet.append(OVStimulation(OpenViBE_stimulation['OVTK_StimulationId_Label_00'] + int(prediction), self.getCurrentTime(), 0.))
        self.output[0].append(stimSet)
    
    def preprocess_data(self, datachunk):
        datachunk = np.abs(np.fft.rfft(datachunk))
        return datachunk

box = MyOVBox()
