import pyaudio
import numpy as np
from pygame import midi


class PolySynth:
    def __init__(self, amp_scale=0.3, max_amp=0.8, sample_rate=44100, num_samples=64):
        # Initialize MIDI
        midi.init()
        if midi.get_count() > 0:
            self.midi_input = midi.Input(midi.get_default_input_id())
        else:
            raise Exception("no midi devices detected")

        # Constants
        self.num_samples = num_samples
        self.sample_rate = sample_rate
        self.amp_scale = amp_scale
        self.max_amp = max_amp

    def _init_stream(self, nchannels):
        # Initialize the Stream object
        self.stream = pyaudio.PyAudio().open(
            rate=self.sample_rate,
            channels=nchannels,
            format=pyaudio.paInt16,
            output=True,
            frames_per_buffer=self.num_samples,
        )

    def _get_samples(self, notes_dict):
        # Return samples in int16 format
        samples = []
        for _ in range(self.num_samples):
            samples.append([next(osc[0]) for _, osc in notes_dict.items()])
        samples = np.array(samples).sum(axis=1) * self.amp_scale
        samples = np.int16(samples.clip(-self.max_amp, self.max_amp) * 32767)
        return samples.reshape(self.num_samples, -1)

    def play(self, osc_function, close=False):
        tempcf = osc_function(1, 1, self.sample_rate)
        has_trigger = hasattr(tempcf, "trigger_release")
        tempsm = self._get_samples({-1: [tempcf, False]})
        nchannels = tempsm.shape[1]
        self._init_stream(nchannels)

        try:
            notes_dict = {}
            while True:
                if notes_dict:
                    # Play the notes
                    samples = self._get_samples(notes_dict)
                    self.stream.write(samples.tobytes())

                if self.midi_input.poll():
                    # Add or remove notes from notes_dict
                    for event in self.midi_input.read(num_events=16):
                        (status, note, vel, _), _ = event
                        if status == 0x80 and note in notes_dict:
                            if has_trigger:
                                notes_dict[note][0].trigger_release()
                                notes_dict[note][1] = True
                            else:
                                del notes_dict[note]

                        elif status == 0x90:
                            freq = midi.midi_to_frequency(note)
                            notes_dict[note] = [
                                osc_function(
                                    freq=freq,
                                    amp=vel / 127,
                                    sample_rate=self.sample_rate,
                                ),
                                False,
                            ]

                if has_trigger:
                    # Delete notes if ended
                    ended_notes = [
                        k for k, o in notes_dict.items() if o[0].ended and o[1]
                    ]
                    for note in ended_notes:
                        del notes_dict[note]

        except KeyboardInterrupt as err:
            self.stream.close()
            if close:
                self.midi_input.close()
