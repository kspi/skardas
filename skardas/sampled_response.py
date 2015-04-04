import csv
import blist
from collections import namedtuple
import math
from . import instrument


def decibels(x):
    return 20 * math.log10(x)


FIELDS = ['frequency', 'reference', 'response', 'phase', 'db']
Sample = namedtuple('Sample', FIELDS)


class SampledResponse:
    INITIAL_SCALE = 0.5

    def __init__(self):
        self.data = blist.sortedlist([], key=lambda x: x.frequency)
        self.scope = instrument.Scope()
        self.generator = instrument.SignalGenerator()

    def release_instruments(self):
        # TODO: actually release the devices
        del self.scope
        del self.generator

    def setup_instruments(self):
        self.scope.reset()
        self.generator.reset()
        yield 0.2

        self.generator.channel(channel=1, on=True)
        yield 0.2
        self.generator.sync(channel=1)
        yield 0.2

        self.scope.chan2_display = False
        yield 0.05
        self.scope.chan1_display = True
        yield 0.05
        self.scope.chan1_offset = 0
        yield 0.05
        self.scope.chan1_scale = self.INITIAL_SCALE
        yield 0.05
        self.scope.trigger_mode = "EDGE"
        yield 0.05
        self.scope.trigger_edge_source = "EXT"
        yield 0.05
        self.scope.trigger_edge_level = 0.1
        yield 0.05
        self.scope.measure_total = True
        yield 0.5

    def adjust_time_scale(self, frequency):
        period = 1 / frequency
        scale = self.scope.timebase_scale  # seconds/screen
        max_scale = period * 2
        min_scale = period * 0.1
        if not (min_scale < scale < max_scale):
            self.scope.timebase_scale = period * 0.2
            yield 0.2
        return self.scope.timebase_scale

    def response_rms(self):
        vpp = self.scope.measure_vpp(channel=1)
        set_scale = False
        while vpp > 1e6:  # an abnormally large value means out of bounds
            self.scope.chan1_scale *= 2
            set_scale = True
            yield 0.5
            vpp = self.scope.measure_vpp(channel=1)
        vrms = self.scope.measure_vrms(channel=1)
        if set_scale:
            self.scope.chan1_scale = self.INITIAL_SCALE
        return vrms

    def sample(self, frequency):
        self.generator.signal(channel=1, frequency=frequency, amplitude=1)
        yield 0.1

        scale = (yield from self.adjust_time_scale(frequency))
        yield scale * 100 + 0.1

        reference = math.sqrt(2) / 2  # Vrms
        response = yield from self.response_rms()

        # TODO: phase calculation and display
        # data = numpy.fromarray(self.scope.capture(channel=1), 'B')
        # phase = determine_phase.sin_phase(data, frequency / self.sampling_rate)
        phase = 0

        db = decibels(response / reference)
        s = Sample(frequency, reference, response, phase, db)
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
