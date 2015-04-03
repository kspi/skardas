import csv
import blist
from collections import namedtuple
import instrument
import time
import math

def decibels(x):
    return 20 * math.log10(x)

FIELDS = ['frequency', 'reference', 'response', 'phase', 'db']
Sample = namedtuple('Sample', FIELDS)

class SampledResponse:
    INITIAL_SCALE = 2

    def __init__(self):
        self.data = blist.sortedlist([], key=lambda x: x.frequency)
        self.scope = instrument.Scope()
        self.generator = instrument.SignalGenerator()

    def release_instruments(self):
        del self.scope
        del self.generator

    def setup_instruments(self):
        self.scope.reset()
        self.generator.reset()
        time.sleep(0.5)

        self.generator.channel(channel=1, on=True)
        time.sleep(0.2)
        self.generator.sync(channel=1)
        time.sleep(0.2)

        self.scope.chan1_display = True
        self.scope.chan1_offset = 0
        self.scope.chan1_scale = self.INITIAL_SCALE
        self.scope.chan2_display = False
        self.scope.trigger_mode = "EDGE"
        self.scope.trigger_edge_source = "EXT"
        self.scope.trigger_level = 0.1
        self.scope.measure_total()
        time.sleep(0.1)

    def adjust_time_scale(self, frequency):
        scale = self.scope.timebase_scale * 6 # seconds/screen
        freq_top = 1 / scale * 0.5
        freq_bottom = freq_top * 1e-3
        if not (freq_bottm < frequency < freq_top):
            self.scope.timebase_scale = 1 / freq_top / 6

    def response_rms(self):
        vpp = self.scope.measure_vpp(channel=1)
        set_scale = False
        while r > 1e6: # an abnormally large value means out of bounds
            self.scope.chan1_scale *= 2
            set_scale = True
            time.sleep(0.1)
            vpp = self.scope.measure_vpp(channel=1)
        vrms = self.scope.measure_vrms(channel=1)
        if set_scale:
            self.scope.chan1_scale = self.INITIAL_SCALE
        return vrms

    def sample(self, frequency):
        self.generator.signal(channel=1, frequency=frequency, amplitude=1)
        time.sleep(0.5)

        self.adjust_scale(frequency)
        time.sleep(0.5) # TODO: increase processing time at low frequencies
        self.scope.force_trigger()
        time.sleep(0.1)

        reference = math.sqrt(2) / 2 #Vrms
        response = self.response_rms()

        ### TODO: phase calculation and display
        #data = numpy.fromarray(self.scope.capture(channel=1), 'B')
        #phase = determine_phase.sin_phase(data, frequency / self.sampling_rate)
        phase = 0
        
        db = decibels(response / reference)
        s = Sample(frequency, reference, response, phase, db)
        print(s)
        self.data.add(s)
        return s

    def frequencies(self):
        return [x.frequency for x in self.data]

    def dbs(self):
        return [x.db for x in self.data]

    def phases(self):
        return [x.phase for x in self.data]

    def write_csv(self, f):
        w = csv.DictWriter(f, FIELDS)
        w.writeheader()
        for x in self.data:
            w.writerow(vars(x))
