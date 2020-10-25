class DFA:
   def __init__(self, states, alphabet, transition_function, start_state, accept_states):
      self.states = states
      self.alphabet = alphabet
      self.transition_function = transition_function
      self.start_state = start_state
      self.accept_states = accept_states
      self.current_state = start_state

   def transition_to_state_with_input(self, input_value):
      if ((self.current_state, input_value) not in self.transition_function.keys()):
         raise Exception("Illegal stimulation input "+OpenViBE_stimulation.keys()[OpenViBE_stimulation.values().index(input_value)]+ " in state "+self.current_state)
         self.current_state = None
      else:
         previous_state = self.current_state
         self.current_state = self.transition_function[(self.current_state, input_value)]
         #print ("Transitioning to state ",self.current_state, " due to stim ",OpenViBE_stimulation.keys()[OpenViBE_stimulation.values().index(input_value)])
         if self.current_state == 'listening':
            #save starttime here
            self.start_time = self.current_stim.date
         elif self.current_state == 'got_label':
            #save label here
            self.label = self.current_stim.identifier
         elif previous_state == 'listening' and self.current_state == 'waiting':
            #calculate duration and push stimulation package to output; 
            self.duration = self.current_stim.date-self.start_time
            #print('outputting '+OpenViBE_stimulation.keys()[OpenViBE_stimulation.values().index(self.label)]+' at date ',self.start_time,' duration ',self.duration)
            # A stimulation set is a chunk which starts at current time and end time is the time step between two calls
            stimSet = OVStimulationSet(self.getCurrentTime(), self.getCurrentTime()+1./self.getClock())
            stimSet.append(OVStimulation(self.label, self.start_time, self.duration))
            self.output[0].append(stimSet)
         elif self.current_state == 'finished':
            stimSet = OVStimulationSet(self.getCurrentTime(), self.getCurrentTime()+1./self.getClock())
            stimSet.append(OVStimulation(32770, self.getCurrentTime(), 0))
            stimSet.append(OVStimulation(33284, self.getCurrentTime(), 0))
            self.output[0].append(stimSet)

class MyOVBox(OVBox, DFA):
   def __init__(self, states, alphabet, transition_function, start_state, accept_states):
      OVBox.__init__(self)
      DFA.__init__(self, states, alphabet, transition_function, start_state, accept_states)
      self.label = None
      self.start_time = None
      self.duration = None
      self.current_stim = None

   def initialize(self):
      # we append to the box output a stimulation header. This is just a header, dates are 0.
      self.output[0].append(OVStimulationHeader(0., 0.))

   def process(self):
      if len(self.input[0]) > 0 and type (self.input[0][0]) == OVStimulationSet:
         while len(self.input[0][0]) > 0:
            self.current_stim = (self.input[0][0].pop())
            self.transition_to_state_with_input(self.current_stim.identifier)

         #dangerous reverse lookup in the stim code dictionary; note that 0x0008100 maps to LabelStart AND Label_00
         #print(OpenViBE_stimulation.keys()[OpenViBE_stimulation.values().index(stim.identifier)])

   def uninitialize(self):
                # we send a stream end.
      end = self.getCurrentTime()
      self.output[0].append(OVStimulationEnd(end, end))  


states = {'idle', 'waiting', 'got_label', 'listening', 'finished'}
            #ExpY,VisYe,VisNo,Lbl00,Lbl01,Lbl02,Lbl03,ExpNo,EOF
alphabet = {32769,32779,32780,33024,33025,33026,33027,32770,33284}
tf = dict()
tf[('idle', 32769)] = 'waiting'
tf[('idle', 33284)] = 'finished'
tf[('waiting', 33024)] = 'got_label' 
tf[('waiting', 33025)] = 'got_label' 
tf[('waiting', 33026)] = 'got_label' 
tf[('waiting', 33027)] = 'got_label' 
tf[('waiting', 32770)] = 'finished'
tf[('waiting', 33284)] = 'finished'
tf[('got_label', 32779)] = 'listening' 
tf[('listening', 32780)] = 'waiting' 

start_state = 'idle';
accept_states = {'finished'};

box = MyOVBox(states, alphabet, tf, start_state, accept_states)