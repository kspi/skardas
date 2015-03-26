import usbtmc

import logging
logger = logging.getLogger(__name__)


class Instrument:
    usbid = None

    def __init__(self):
        assert self.usbid
        self.instrument = usbtmc.Instrument(*self.usbid)
        self.name = self.idn()
        self.reset()
        self.wait()

    def idn(self):
        return self.ask("*IDN?")

    def reset(self):
        return self.write("*RST")

    def wait(self):
        self.write("*WAI")

    def write(self, cmd, *args, **kwargs):
        line = cmd.format(*args, **kwargs)
        logger.debug("{}: {}".format(self.name, line))
        self.instrument.write(line)

    def ask(self, cmd, *args, **kwargs):
        line = cmd.format(*args, **kwargs)
        logger.debug("{}: {}".format(self.name, line))
        return self.instrument.ask(line)


def on_off(x):
    if x:
        return "ON"
    else:
        return "OFF"


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

    def get_sampling_rate(self, channel=1):
        assert(channel in [1, 2])
        return float(self.ask(":ACQ:SAMP? CHAN{}", channel))

    def acquire(self, type="NORM", mode="RTIM", averages=16, memdepth="LONG"):
        """
        Configure acquisition.
        <type> could be NORMal, AVERage or PEAKdetect.
        <mode> could be RTIMe (Real time Sampling) or ETIMe (Equivalent Sampling).
        <averages> could be and integer of 2 times the power of N within 2 and 256.
        <depth> could be LONG (long memory) or NORMal (normal memory).
        """
        assert(type in ["NORM", "AVER", "PEAK"])
        assert(mode in ["RTIM", "ETIM"])
        assert(averages in [2**x for x in range(1, 9)])
        assert(depth in ["LONG", "NORM"])
        self.write(":ACQ:TYPE {}", type)
        self.write(":ACQ:MODE {}", mode)
        self.write(":ACQ:AVER {}", averages)
        self.write(":ACQ:MEMD {}", memdepth)
        self.wait()

    def timebase(self, mode="MAIN", format="XY", offset=0, scale=1):
        """
        Configure timebase.

        <mode> could be MAIN (main timebase) or DELayed (delayed scan).

        <format> could be XY, YT or SCANning.

        Offset of the waveform position relative to the trigger midpoint.). Thereinto,
        In NORMAL mode, the range of <scale_val> is 1s ~ end of the memory;
        In STOP mode, the range of <scale_val> is -500s ~ +500s;
        In SCAN mode, the range of <scale_val> is -6*Scale ~ +6*Scale; (Note: Scale
        indicates the current horizontal scale, the unit is s/div.)

        For scale, the unit is s/div (seconds/grid):
        In YT mode, the range of <scale_val> is 2ns - 50s;
        In ROLL mode, the range of <scale_val> is 500ms - 50s;
        """
        assert(mode in ["MAIN", "DEL"])
        assert(format in ["XY", "YT", "SCAN"])
        tbcmd = "" if mode == "MAIN" else ":DEL"
        self.write(":TIM:MODE {}", mode)
        self.write(":TIM:FORM {}", format)
        self.write(":TIM{}:OFFS {}", tbcmd, offset)
        self.write(":TIM{}:SCAL {}", tbcmd, scale)
        self.wait()

    def trigger(self, mode="EDGE", source="CHAN1", level=0, sweep="NORMAL"):
        """
        <mode> could be EDGE, PULSe.

        <source> could be the input
        channel (CHANnel1, CHANnel2), external trigger channel (EXT), AC Line (Mains
        supply).
        In EDGE mode, <src> could be CHANnel<n>, EXT, ACLine;
        In PULSe mode, <src> could be CHANnel<n>, EXT.

        <level> range is: -6*Scale~+6*Scale, Scale indicates the current vertical
        scale, the unit is V/div.

        <sweep> is AUTO, NORMAL, SINGLE
        """
        assert(mode in ["EDGE", "PULS"])
        self.write(":TRIG:MODE", mode)
        self.write(":TRIG:{}:SOUR {}", mode, source)
        self.write(":TRIG:{}:LEV {}", mode, level)
        self.write(":TRIG:{}:SWE {}", mode, sweep)
        self.wait()

    def channel(self, channel=1, display=True, coupling="DC", offset=0, probe=1, scale=1):
        """
        Configure <channel>.

        <coupling> can be DC, AC, GND.

        <probe> can be 1, 5, 10, 50, 100, 500 or 1000.

        When the Probe is set to 1X, the range of <scale> is 2mV ~ 10V;
        When the Probe is set to 5X, the range of <scale> is 10mV ~50V;
        When the Probe is set to 10X, the range of <scale> is 20mV ~ 100V;
        When the Probe is set to 50X, the range of <scale> is 100mV ~ 500V;
        When the Probe is set to 100X, the range of <scale> is 200mV ~ 1000V;
        When the Probe is set to 500X, the range of <scale> is 1V ~5000V;
        When the Probe is set to 1000X, the range of <scale> is 2V~ 10000V.

        When Scale≥250mV, the range of <offset>is -40V~+40V;
        When Scale<250mV, the range of <offset>is -2V~+2V.
        """
        assert(channel in [1, 2])
        self.write(":CHAN{}:DISP {}", on_off(display))
        self.write(":CHAN{}:COUP {}", coupling)
        self.write(":CHAN{}:PROB {}", probe)
        self.write(":CHAN{}:SCAL {}", scale)
        self.write(":CHAN{}:OFFS {}", offset)
        self.wait()

    def measure_total(self, on=True):
        self.write(":MEAS:TOT {}", on_off(on))
        self.wait()

    def measure_vpp(self, channel=1):
        assert(channel in [1, 2])
        return float(self.ask(":MEAS:VPP?"))

    def measure_vmax(self, channel=1):
        assert(channel in [1, 2])
        return float(self.ask(":MEAS:VMAX?"))

    def measure_vmin(self, channel=1):
        assert(channel in [1, 2])
        return float(self.ask(":MEAS:VMIN?"))

    def measure_vamplitude(self, channel=1):
        assert(channel in [1, 2])
        return float(self.ask(":MEAS:VAMP?"))

    def measure_vrms(self, channel=1):
        assert(channel in [1, 2])
        return float(self.ask(":MEAS:VRMS?"))

    def measure_frequency(self, channel=1):
        assert(channel in [1, 2])
        return float(self.ask(":MEAS:FREQ?"))


class SignalGenerator(Instrument):
    """Siglent SDG1010"""

    usbid = (0xf4ed, 0xee3a)

    def channel(self, channel=1, on=True, load=50):
        """Load is HZ (high-Z) or a number of Ohms."""
        self.write("C{}:OUTP {},LOAD,{}", on_off(on), load)
        self.wait()

    def signal(self, channel=1, type="SINE", frequency=440, amplitude=2, offset=0, phase=0):
        """Phase is in degrees, frequency in Hz, amplitude and offset in V.

        Type is one of SINE, SQUARE, RAMP, PULSE, NOISE, ARB, DC."""

        self.write("C{}:BSWV WVTP,{},FRQ,{},AMP,{},OFST,{},PHSE,{}", channel, type, frequency, amplitude, offset, phase)
        self.wait()

    def sweep(self, channel=1, time=1, start=220, stop=440):
        self.write("C{}:SWWV STATE,ON,TIME,{}S,DIR,{},START,{},STOP,{},SOURCE,MAN,MTRIG",
                channel, time, "UP" if start <= stop else "DOWN", start, stop)
        self.wait()

    def sync(self, channel=1, on=True):
        self.write("C{}:SYNC {}", on_off(on))
        self.wait()
