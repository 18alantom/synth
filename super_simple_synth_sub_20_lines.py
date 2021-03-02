import pyaudio
import numpy as np
from math import pi, sin
from pygame import midi
from itertools import count
midi.init()
mi=midi.Input(device_id=midi.get_default_input_id())
st=pyaudio.PyAudio().open(44100,1,pyaudio.paInt16,output=True,frames_per_buffer=256)
try:
  nd={}
  while True:
    if nd:st.write(np.int16([sum([int(next(osc)*32767) for _,osc in nd.items()]) for _ in range(256)]).tobytes())
    if mi.poll():
      for(s,n,v,_),_ in mi.read(16):
        if s==0x80 and n in nd:del nd[n]
        elif s==0x90 and n not in nd:nd[n]=(sin(c)*v*0.1/127 for c in count(0,(2*pi*midi.midi_to_frequency(n))/44100))
except KeyboardInterrupt as err:
  mi.close()
  st.close()
