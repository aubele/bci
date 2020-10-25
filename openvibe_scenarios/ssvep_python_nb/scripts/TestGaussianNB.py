

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
        
        self.gnbs = [None for x in range(3)]
        self.signalHeaders = [None for x in range(3)]
        self.predictions = [1, 1, 1]


    def initialize(self):
        self.gnbs[0] = joblib.load(self.setting["Classifier_Dir"] + "/python_gnb_1.pkl")
        self.gnbs[1] = joblib.load(self.setting["Classifier_Dir"] + "/python_gnb_2.pkl")
        self.gnbs[2] = joblib.load(self.setting["Classifier_Dir"] + "/python_gnb_3.pkl")
        
    def process(self):
        #signals
        for signalIndex in range(3):
            signalInput = self.input[signalIndex]
            for chunkIndex in range(len(signalInput)):
                if(type(signalInput[chunkIndex]) == OVSignalHeader):
                    signalHeader = signalInput.pop()
                    self.signalHeaders[signalIndex] = signalHeader
                    
                elif(type(signalInput[chunkIndex])  == OVSignalBuffer):
                    chunk = signalInput.pop()

                    numpyBuffer = np.array(chunk, dtype=np.float64).reshape(tuple(self.signalHeaders[signalIndex].dimensionSizes))

                    preprocessedData = self.preprocess_data(numpyBuffer).reshape(1, -1)

                    self.classify_chunk(preprocessedData, signalIndex)

                elif(type(signalInput[chunkIndex])  == OVSignalEnd):
                    pass
            self.final_prediction()
        return

    def uninitialize(self):
        return

    def classify_chunk(self, preprocesseddata, index):
        self.predictions[index] = self.gnbs[index].predict(preprocesseddata)
        
    def final_prediction(self):
        if(self.predictions.count(0) == 1):
            self.send_result_stim(self.predictions.index(0) + 1)
        self.send_result_stim(0)
        

    def preprocess_data(self, datachunk):
        # Same preproccesing as openvibe ssvep example
        # (logarithmic band power)
        datachunk = np.square(datachunk)
        datachunk = np.mean(datachunk, axis=1)
        datachunk = datachunk + 1
        datachunk = np.log(datachunk)
        
        return datachunk

    def send_result_stim(self, result):
        stimSet = OVStimulationSet(self.getCurrentTime(), self.getCurrentTime()+1./self.getClock()) 
        stimSet.append(OVStimulation(OpenViBE_stimulation['OVTK_StimulationId_Label_0' + str(result)], self.getCurrentTime(), 0.))
        self.output[0].append(stimSet)

box = MyOVBox()
