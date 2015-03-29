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
    def __init__(self):
        self.data = blist.sortedlist([], key=lambda x: x.frequency)
        self.scope = instrument.Scope()
        self.generator = instrument.SignalGenerator()

    def setup_instruments(self):
        self.scope.reset()
        self.generator.reset()
        time.sleep(0.5)

        self.generator.signal(channel=1, frequency=440, amplitude=3)
        time.sleep(0.5)
        self.generator.channel(channel=1, on=True)
        time.sleep(0.5)
        self.generator.sync(channel=1)
        time.sleep(0.5)

        self.scope.auto()
        time.sleep(6)

        self.scope.trigger(source='EXT', level=0.1)
        self.scope.measure_total()


    def release_instruments(self):
        # TODO: implement
        pass


    def sample(self, frequency):
        self.generator.signal(channel=1, frequency=frequency, amplitude=1)
        time.sleep(0.5)

        reference = 2 #Vpp
        response = self.scope.measure_vpp(channel=1)

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
