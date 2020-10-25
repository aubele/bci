import numpy as np
from sklearn.externals import joblib
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB

from lasagne.layers import DenseLayer, InputLayer, DropoutLayer, Conv1DLayer, MaxPool1DLayer
from lasagne.nonlinearities import softmax, rectify
from lasagne.updates import adam, nesterov_momentum
from lasagne.random import set_rng

from nolearn.lasagne import NeuralNet, TrainSplit, objective

from imblearn.under_sampling import RandomUnderSampler 

import sys
import os

"""This script is used in a OpenVibe Python scripting box.
With this script you can train a CNN for classification of SSVEP Data.
"""

__license__ = "MIT"
__author__  = "timo.wilhelm1@hs-augsburg.de"

RANDOM_STATE = 42

if not ('OVBox' in vars() or 'OVBox' in globals()):
    from openvibe import *

class MyOVBox(OVBox):
    def __init__(self):
        OVBox.__init__(self)
        self.currentStimulationTarget = 0
        self.currentStimulationEndTime = None
        self.data = []
        self.targets = []
        self.signalHeader = None

    def initialize(self):
        self.currentStimulationTargetTime = self.getCurrentTime()

    def process(self):
        #stims
        stimInput = self.input[1]
        for chunkIdx in range(len(stimInput)):
            chunk = stimInput.pop()
            if type(chunk) == OVStimulationSet:
                for stimIdx in range(len(chunk)):
                    stim = chunk.pop()
                    if stim.identifier == OpenViBE_stimulation['OVTK_StimulationId_ExperimentStop']:
                        self.start_training()
                    else:
                        self.currentStimulationTargetTime = self.getCurrentTime()
                        self.currentStimulationEndTime = self.getCurrentTime() + float(stim.duration)
                        self.currentStimulationTarget = stim.identifier - OpenViBE_stimulation['OVTK_StimulationId_Label_00']

        if self.getCurrentTime() > self.currentStimulationEndTime:
            self.currentStimulationTarget = 0

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

            elif type(signalInput[chunkIndex]) == OVSignalEnd:
                    pass

    def uninitialize(self):
        return

    def start_training(self):
        
        rand = np.random.RandomState(RANDOM_STATE)
        set_rng(rand)
        self.data = np.array(self.data, dtype=np.float32)
        nsamples, nx, ny = self.data.shape

        # Undersample the data to get even sample spaces
        self.data = self.data.reshape((nsamples,nx*ny))
        ros = RandomUnderSampler(random_state=RANDOM_STATE)
        self.data, self.targets = ros.fit_sample(self.data, self.targets)

        X_train = np.array(self.data, dtype=np.float32).reshape((-1, nx, ny))
        y_train = np.array(self.targets, dtype=np.int32)    

        unique_items, counts = np.unique(y_train, return_counts=True)
        print(unique_items)
        print(counts)
        
        # CNN with Dropout. Pooling  omitted becuase of small (8-Channel) dimension size.
        layers0 = [
                 # layer dealing with the input data
                (InputLayer, {'shape': (None, X_train.shape[1], X_train.shape[2])}),

                # hidden Layers
                (Conv1DLayer, {'num_filters': 12, 'filter_size': 3, 'pad':'same', 'stride':1, 'nonlinearity':rectify}),
                (Conv1DLayer, {'num_filters': 12, 'filter_size': 3, 'pad':'same', 'stride':1, 'nonlinearity':rectify}),
                (DenseLayer, {'num_units': 128, 'nonlinearity':rectify}),
                (DenseLayer, {'num_units': 64, 'nonlinearity':rectify}),
                (DropoutLayer, {}),
                # the output layer
                (DenseLayer, {'num_units': 4, 'nonlinearity': softmax}),
            ]

        
        self.clf = NeuralNet(
            layers=layers0,
            max_epochs=200,
            update=adam,
            verbose=1,
        )
        print("Starting classificator training with " + str(y_train.size) + " samples.")

        # uncomment the following two lines to save the final classification training data

        np.save(self.setting["output"] + os.sep + "x_train_data", X_train)
        np.save(self.setting["output"] + os.sep + "y_train_data", y_train)
        self.clf.fit(X_train, y_train)

        sys.setrecursionlimit(10000)
        joblib.dump(self.clf, self.setting["output"] + "/clf.pkl")
        print("training done!") 
        self.send_stop_stim()

    def preprocess_data(self, datachunk):
        # transform data to real part of fourier transformation to extract the frequency peaks
        datachunk = np.abs(np.fft.rfft(datachunk))
        return datachunk

    def send_stop_stim(self):
        stimSet = OVStimulationSet(self.getCurrentTime(), self.getCurrentTime()+1./self.getClock()) 
        stimSet.append(OVStimulation(OpenViBE_stimulation['OVTK_StimulationId_Label_00'], self.getCurrentTime(), 0.))
        self.output[0].append(stimSet)

box = MyOVBox()
