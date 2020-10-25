# for better IDE Support
if not ('OVBox' in vars() or 'OVBox' in globals()):
    from openvibe import *
if not ('OpenViBE_stimulation' in vars() or 'OpenViBE_stimulation' in globals()):
    from StimulationsCodes import *


# stimSet = OVStimulationSet(self.getCurrentTime(), self.getCurrentTime()+1./self.getClock())
# stimSet.append(OVStimulation(self.label, self.start_time, self.duration))

class ConverterBox(OVBox):
    def __init__(self):
        OVBox.__init__(self)
        self.state_iterator = None

    def initialize(self):
        # we append to the box output a stimulation header. This is just a header, dates are 0.
        self.output[0].append(OVStimulationHeader(0., 0.))
        self.state_iterator = get_state_coroutine(self.output[0], self.getClock())

    def process(self):
        for chunkIdx in range(len(self.input[0])):
            chunk = self.input[0].pop()
            if type(chunk) == OVStimulationSet:
                for _ in range(len(chunk)):
                    self.state_iterator.send(chunk.pop())

    def uninitialize(self):
        # we send a stream end.
        end = self.getCurrentTime()
        self.output[0].append(OVStimulationEnd(end, end))



def get_state_coroutine(output, clock_rate):
    reverse_label_dict = {v: k for k, v in OpenViBE_stimulation.items()}
    identifier_stim_0 = OpenViBE_stimulation['OVTK_StimulationId_Label_00']
    identifier_stim_1F = OpenViBE_stimulation['OVTK_StimulationId_Label_1F']
    identifier_ex_stop = OpenViBE_stimulation['OVTK_StimulationId_ExperimentStop']
    identifier_eof = OpenViBE_stimulation['OVTK_StimulationId_EndOfFile']

    def coroutine():
        stim = (yield)
        assert(stim.identifier == OpenViBE_stimulation['OVTK_StimulationId_ExperimentStart'])
        while True:
            label_stim = (yield)
            if identifier_stim_0 <= label_stim.identifier <= identifier_stim_1F:
                start_stim = (yield)
                assert(start_stim.identifier == OpenViBE_stimulation['OVTK_StimulationId_VisualStimulationStart'])
                stop_stim = (yield)
                assert(stop_stim.identifier == OpenViBE_stimulation['OVTK_StimulationId_VisualStimulationStop'])
                stim_set = OVStimulationSet(start_stim.date, start_stim.date + 1. / clock_rate)
                stim_set.append(OVStimulation(label_stim.identifier, start_stim.date,
                                              stop_stim.date - start_stim.date))
                output.append(stim_set)
            elif label_stim.identifier == identifier_eof or label_stim.identifier == identifier_ex_stop:
                stim_set = OVStimulationSet(label_stim.date, label_stim.date + 2. / clock_rate)
                stim_set.append(OVStimulation(identifier_ex_stop, label_stim.date, 0))
                stim_set.append(OVStimulation(identifier_eof, label_stim.date + 1. / clock_rate, 0))
                output.append(stim_set)
                print("Appended Experiment Stop and EOF")

    c = coroutine()
    next(c)
    return c

box = ConverterBox()
