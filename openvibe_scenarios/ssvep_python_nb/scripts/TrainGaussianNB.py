

#from openvibe import *
#from StimulationsCodes import  OpenViBE_stimulation

import numpy as np
import os
from sklearn import preprocessing
from sklearn.naive_bayes import GaussianNB

from sklearn.externals import joblib


class MyOVBox(OVBox):
    def __init__(self):
        
        OVBox.__init__(self)
        
        self.signalHeaders = [None for i in range(6)]
        self.processedSignalChunks = [[] for i in range(6)]

        self.gnb1 = GaussianNB()
        self.gnb2 = GaussianNB()
        self.gnb3 = GaussianNB()


    def initialize(self):
        return
        
    def process(self):
        #signals
        for signalIndex in range(6):
            signalInput = self.input[signalIndex]
            for chunkIndex in range(len(signalInput)):
                if(type(signalInput[chunkIndex]) == OVSignalHeader):
                    signalHeader = signalInput.pop()
                    self.signalHeaders[signalIndex] = signalHeader
                    
                elif(type(signalInput[chunkIndex])  == OVSignalBuffer):
                    chunk = signalInput.pop()

                    numpyBuffer = np.array(chunk, dtype=np.float64).reshape(tuple(self.signalHeaders[signalIndex].dimensionSizes))

                    preprocessedData = self.preprocess_data(numpyBuffer)
                    self.processedSignalChunks[signalIndex].append(preprocessedData)

                elif(type(signalInput[chunkIndex])  == OVSignalEnd):
                    pass
        

        #stims

        stimInput = self.input[6]
        for chunkIdx in range(len(stimInput)):
            chunk=stimInput.pop()
            if (type(chunk) == OVStimulationSet):
                for stimIdx in range(len(chunk)):
                    stim = chunk.pop()
                    if stim.identifier == OpenViBE_stimulation['OVTK_StimulationId_ExperimentStop']:
                        print("Starting Classificator Training")
                        self.start_training()
                        pass
        return

    def uninitialize(self):
        return

    def start_training(self):
        data1 = np.array(self.processedSignalChunks[0] + self.processedSignalChunks[1], dtype=np.float64)
        target1 = np.array(len(self.processedSignalChunks[0]) * [0] + len(self.processedSignalChunks[1]) * [1])

        data2 = np.array(self.processedSignalChunks[2] + self.processedSignalChunks[3], dtype=np.float64)
        target2 = np.array(len(self.processedSignalChunks[2]) * [0] + len(self.processedSignalChunks[3]) * [1])

        data3 = np.array(self.processedSignalChunks[4] + self.processedSignalChunks[5], dtype=np.float64)
        target3 = np.array(len(self.processedSignalChunks[4]) * [0] + len(self.processedSignalChunks[5]) * [1])

        self.gnb1.fit(data1, target1)
        self.gnb2.fit(data2, target2)
        self.gnb3.fit(data3, target3)

        joblib.dump(self.gnb1, self.setting["output"] + "/python_gnb_1.pkl")
        joblib.dump(self.gnb2, self.setting["output"] + "/python_gnb_2.pkl")
        joblib.dump(self.gnb3, self.setting["output"] + "/python_gnb_3.pkl")

        self.send_stop_stim()

    
    def preprocess_data(self, datachunk):
        # Same preproccesing as openvibe ssvep example
        # (logarithmic band power)
        datachunk = np.square(datachunk)
        datachunk = np.mean(datachunk, axis=1)
        datachunk = datachunk + 1
        datachunk = np.log(datachunk)
        
        return datachunk

    def send_stop_stim(self):
        stimSet = OVStimulationSet(self.getCurrentTime(), self.getCurrentTime()+1./self.getClock()) 
        stimSet.append(OVStimulation(OpenViBE_stimulation['OVTK_StimulationId_Label_00'], self.getCurrentTime(), 0.))
        self.output[0].append(stimSet)

box = MyOVBox()
