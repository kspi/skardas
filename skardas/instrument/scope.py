from .instrument import Instrument


def scope_property_enum(command, choices, returned_choices=None, type=str):
    to_choice = dict(zip(returned_choices or choices, choices))

    def fget(self):
        return type(self.ask("{}?", command))

    def fset(self, value):
        self.write("{} {}", command, to_choice[type(value)])

    doc = """
    The enum property {command}.

    Possible values are: {choices_str}
    """.format(command=command, choices_str=", ".join(str(k) for k in to_choice.keys()))

    return property(fget, fset, doc=doc)


def scope_property_bool(command, on="ON", off="OFF"):
    def fget(self):
        return self.ask("{}?", command) == on

    def fset(self, value):
        self.write("{} {}", command, on if value else off)

    doc = """
    The boolean property {command}.
    """.format(command=command)

    return property(fget, fset, doc=doc)


def scope_property_number(command, units):
    def fget(self):
        return float(self.ask("{}?", command))

    def fset(self, value):
        self.write("{} {:.10f}", command, float(value))

    doc = """
    The numeric {command} property. The value is in {units}.
    """.format(command=command, units=units)

    return property(fget, fset, doc=doc)


class Scope(Instrument):
    """Rigol DS1052E"""

    usbid = (0x1ab1, 0x0588)

    def capture(self, channel=1):
        assert(channel in [1, 2])
        return self.instrument.ask_raw(b":WAV:DATA? CHAN{}", channel)

    def run(self):
        self.write(":RUN")

    def stop(self):
        self.write(":STOP")

    def auto(self):
        self.write(":AUTO")

    def force_trigger(self):
        self.write(":FORC")

    def local(self):
        self.write(":KEY:FORCe")

    acquire_type = scope_property_enum(":ACQ:TYPE", ["NORM", "AVER", "PEAK"], ["NORMAL", "AVERAGE", "PEAKDETECT"])
    acquire_mode = scope_property_enum(":ACQ:MODE", ["RTIM", "ETIM"], ["REAL_TIME", "EQUAL_TIME"])
    acquire_averages = scope_property_enum(":ACQ:AVER", [2**x for x in range(1, 9)], type=int)
    acquire_memdepth = scope_property_enum(":ACQ:MEMD", ["LONG", "NORM"], ["LONG", "NORMAL"])

    timebase_mode = scope_property_enum(":TIM:MODE", ["MAIN", "DEL"], ["MAIN", "DELAYED"])
    timebase_format = scope_property_enum(":TIM:FORM", ["XY", "YT", "SCAN"], ["X-Y", "Y-T", "SCANNING"])
    timebase_scale = scope_property_number(":TIM:SCAL", units="seconds/division")
    timebase_offset = scope_property_number(":TIM:OFFS", units="seconds")
    timebase_delayed_format = scope_property_enum(":TIM:DEL:FORM", ["XY", "YT", "SCAN"], ["X-Y", "Y-T", "SCANNING"])
    timebase_delayed_scale = scope_property_number(":TIM:DEL:SCAL", units="seconds/division")
    timebase_delayed_offset = scope_property_number(":TIM:DEL:OFFS", units="seconds")

    trigger_mode = scope_property_enum(":TRIG:MODE",
            ["EDGE", "PULS", "VIDEO", "SLOP", "PATT", "DUR", "ALT"],
            ["EDGE", "PULSE", "VIDEO", "SLOPE", "PATTERN", "DURATION", "ALTERNATION"])
    trigger_edge_source = scope_property_enum(":TRIG:EDGE:SOUR",
            ["CHAN1", "CHAN2", "EXT", "AC"],
            ["CH1", "CH2", "EXT", "ACLINE"])
    trigger_edge_level = scope_property_number(":TRIG:EDGE:LEV", "V")
    trigger_edge_sweep = scope_property_enum(":TRIG:EDGE:SWE",
            ["AUTO", "NORM", "SING"],
            ["AUTO", "NORMAL", "SINGLE"])
    trigger_edge_coupling = scope_property_enum(":TRIG:EDGE:COUP",
            ["DC", "AC", "HF", "LF"])

    chan1_bwlimit = scope_property_bool(":CHAN1:BWL")
    chan1_display = scope_property_bool(":CHAN1:DISP", on="1", off="0")
    chan1_invert = scope_property_bool(":CHAN1:INV")
    chan1_filter = scope_property_bool(":CHAN1:FILT")
    chan1_coupling = scope_property_enum(":CHAN1:COUP", ["DC", "AC", "GND"])
    chan1_offset = scope_property_number(":CHAN1:OFFS", "V")
    chan1_scale = scope_property_number(":CHAN1:SCAL", "V")
    chan1_probe = scope_property_enum(":CHAN1:PROB", [1, 5, 10, 50, 100, 500, 1000], type=int)

    chan2_bwlimit = scope_property_bool(":CHAN2:BWL")
    chan2_display = scope_property_bool(":CHAN2:DISP", on="1", off="0")
    chan2_invert = scope_property_bool(":CHAN2:INV")
    chan2_filter = scope_property_bool(":CHAN2:FILT")
    chan2_coupling = scope_property_enum(":CHAN2:COUP", ["DC", "AC", "GND"])
    chan2_offset = scope_property_number(":CHAN2:OFFS", "V")
    chan2_scale = scope_property_number(":CHAN2:SCAL", "V")
    chan2_probe = scope_property_enum(":CHAN2:PROB", [1, 5, 10, 50, 100, 500, 1000], type=int)

    measure_total = scope_property_bool(":MEAS:TOT")

    def measure_vpp(self, channel=1):
        assert(channel in [1, 2])
        return float(self.ask(":MEAS:VPP? CHAN{}".format(channel)))

    def measure_vmax(self, channel=1):
        assert(channel in [1, 2])
        return float(self.ask(":MEAS:VMAX? CHAN{}".format(channel)))

    def measure_vmin(self, channel=1):
        assert(channel in [1, 2])
        return float(self.ask(":MEAS:VMIN? CHAN{}".format(channel)))

    def measure_vamplitude(self, channel=1):
        assert(channel in [1, 2])
        return float(self.ask(":MEAS:VAMP? CHAN{}".format(channel)))

    def measure_vrms(self, channel=1):
        assert(channel in [1, 2])
        return float(self.ask(":MEAS:VRMS? CHAN{}".format(channel)))

    def measure_frequency(self, channel=1):
        assert(channel in [1, 2])
        return float(self.ask(":MEAS:FREQ? CHAN{}".format(channel)))
