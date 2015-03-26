import csv
import blist
from collections import namedtuple
import instrument
import time

def decibels(x):
    return 20 * log10(x)

FIELDS = ['frequency', 'reference', 'response', 'phase', 'db']
Sample = namedtuple('Sample', FIELDS)

class SampledResponse:
    def __init__(self):
        self.data = sortedlist([], key=lambda x: x.frequency)
        self.scope = instrument.Scope()
        self.generator = instrument.SignalGenerator()

    def setup_instruments(self):
        self.scope.reset()
        self.scope.trigger(source='EXT', level=1)
        self.scope.measure_total()
        self.scope.wait()
        self.sampling_rate = self.scope.get_sampling_rate()
        self.generator.reset()
        self.generator.sync(channel=1)
        self.generator.wait()

    def sample(self, frequency):
        self.generator.signal(channel=2, frequency=frequency, amplitude=6)
        self.generator.signal(channel=1, frequency=frequency, amplitude=6)
        time.sleep(0.01)
        while abs(1 - self.scope.measure_frequency(channel=2) / frequency) > 1e-3):
            time.sleep(0.01)
        reference = self.scope.measure_vrms(channel=2)
        response = self.scope.measure_vrms(channel=1)

        ### TODO: phase calculation and display
        #data = numpy.fromarray(self.scope.capture(channel=1), 'B')
        #phase = determine_phase.sin_phase(data, frequency / self.sampling_rate)
        
        db = decibels(response / reference)
        self.data.add(Sample(frequency, reference, response, phase, db))

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
