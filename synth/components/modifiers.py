"""
Components that have __call__ implemented and whose
instances can be used as functions to alter the output
of any kind of generator. Generally used in a Chain
component.
"""

from collections.abc import Iterable

class Panner:
    """
    Will convert a mono input into stereo.
    """
    def __init__(self, r=0.5):
        """
        r : is the right pan value, 0 means 100% left
            panned and 1 means 100% right panned, 0.5
            is center panned.
        """
        self.r = r
        
    def __call__(self, val):
        r = self.r * 2
        l = 2 - r
        return (l * val, r * val)
      
class ModulatedPanner(Panner):
    """
    Same as the Panner but takes in a modulator
    to set the internal `r` value.
    """
    def __init__(self, modulator):
        """
        modulator : any kind of generator that returns a
            value within the range of [-1, 1] this is used
            to set the `r` value that has a range of [0, 1]
        """
        super().__init__(r=0)
        self.modulator = modulator
        
    def __iter__(self):
        iter(self.modulator)
        return self
    
    def __next__(self):
        self.r = (next(self.modulator) + 1) / 2
        return self.r

class Volume:
    """
    Scales the input values by `amp`, can be used
    to increase or decrease the amplitude.
    """
    def __init__(self, amp=1.):
        """
        amp : sets the amplitude multiplier for the 
            input signal (1 : no change, 0 : no output).
        """
        self.amp = amp
        
    def __call__(self, val):
        _val = None
        if isinstance(val, Iterable):
            _val = tuple(v * self.amp for v in val)
        elif isinstance(val, (int, float)):
            _val = val * self.amp
        return _val

class ModulatedVolume(Volume):
    """
    Same as the volume component but the
    internal `amp` is set by a modulator.
    """
    def __init__(self, modulator):
        """
        modulator : any kind of generator that returns a
            value within the range of [0, max_amp] this is used
            to set the `amp` value directly. If max_amp is > 1
            then the amplitude of the input will increase.
        """
        super().__init__(0.)
        self.modulator = modulator
        
    def __iter__(self):
        iter(self.modulator)
        return self
    
    def __next__(self):
        self.amp = next(self.modulator)
        return self.amp
    
    def trigger_release(self):
        if hasattr(self.modulator, "trigger_release"):
            self.modulator.trigger_release()
    
    @property
    def ended(self):
        ended = False
        if hasattr(self.modulator, "ended"):
            ended = self.modulator.ended
        return ended
      
class Clipper:
    """
    Component that clips the input signal to 
    the given wave range.
    """
    def __init__(self, wave_range=(-1,1)):
        """
        wave_range : tuple of (min, max) values which are
            used to clip the input signal.
        """
        mi, ma = wave_range
        self.mm = lambda v: max(mi, min(ma, v))
        
    def __call__(self, val):
        if isinstance(val, Iterable):
            _val = tuple(self.mm(v/2)*2 for v in val)
        else:
            _val = self.mm(val)
        return _val