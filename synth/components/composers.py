"""
Components that help in composing combinations of generators and modifiers
to generate waves of different kinds.
"""

from collections.abc import Iterable

class Chain:
    """
    A component that allows for chaining a single
    generator with multiple modifiers after it.

    For sequential composition of waves.
    """
    def __init__(self, generator, *modifiers):
        """
        generator : instance of an Oscillator or
          anything else that can generate a sequence of numbers
          by using __iter__ and __next__.
        
        modifiers : Any function that takes in a value
          modifies it and returns another value.
          example : instances of Panner.
        """
        self.generator = generator
        self.modifiers = modifiers
        
    def __getattr__(self, attr):
        val = None
        if hasattr(self.generator, attr):
            val = getattr(self.generator, attr)
        else:
            for modifier in self.modifiers:
                if hasattr(modifier, attr):
                    val = getattr(modifier, attr)
                    break
            else:
                raise AttributeError(f"attribute '{attr}' does not exist")
        return val
    
    def trigger_release(self):
        tr = "trigger_release"
        if hasattr(self.generator, tr):
            self.generator.trigger_release()
        for modifier in self.modifiers:
            if hasattr(modifier, tr):
                modifier.trigger_release()
                
    @property
    def ended(self):
        ended = []; e = "ended"
        if hasattr(self.generator, e):
            ended.append(self.generator.ended)
        ended.extend([m.ended for m in self.modifiers if hasattr(m, e)])
        return all(ended)
    
    def __iter__(self):
        iter(self.generator)
        [iter(mod) for mod in self.modifiers if hasattr(mod, "__iter__")]
        return self
        
    def __next__(self):
        val = next(self.generator)
        [next(mod) for mod in self.modifiers if hasattr(mod, "__iter__")]
        for modifier in self.modifiers:
            val = modifier(val)
        return val


class WaveAdder:
    """
    Component that returns the mean of the output
    of multiple generators.

    For parallel composition of waves.
    """
    def __init__(self, *generators, stereo=False):
        """
        generator : instance of an Oscillator or
            anything else that can generate a sequence of numbers
            by using __iter__ and __next__.

        stereo : if True the output will have a tuple of two 
            numbers for the left and the right channel each,
            else only one number.
        """
        self.generators = generators
        self.stereo = stereo
        
    def _mod_channels(self, _val):
        val = _val
        if isinstance(_val, (int, float)) and self.stereo:
            val = (_val, _val)
        elif isinstance(_val, Iterable) and not self.stereo:
            val = sum(_val)/len(_val)
        return val
    
    def trigger_release(self):
        [gen.trigger_release() for gen in self.generators if hasattr(gen, "trigger_release")]
    
    @property
    def ended(self):
        ended = [gen.ended for gen in self.generators if hasattr(gen, "ended")]
        return all(ended)
    
    def __iter__(self):
        [iter(gen) for gen in self.generators]
        return self
            
    def __next__(self):
        vals = [self._mod_channels(next(gen)) for gen in self.generators]
        if self.stereo:
            l, r = zip(*vals)
            val = (sum(l)/len(l), sum(r)/len(r))
        else:
            val = sum(vals)/ len(vals)
        return val