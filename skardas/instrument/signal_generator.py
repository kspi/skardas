from .instrument import Instrument


class SignalGenerator(Instrument):
    """Siglent SDG1010"""

    usbid = (0xf4ed, 0xee3a)

    def channel(self, channel=1, on=True, load=50):
        """Load is HZ (high-Z) or a number of ohms."""
        self.write("C{}:OUTP {},LOAD,{}", channel, "ON" if on else "OFF", load)

    def signal(self, channel=1, type="SINE", frequency=440, amplitude=2, offset=0, phase=0):
        """Phase is in degrees, frequency in Hz, amplitude and offset in V.

        Type is one of SINE, SQUARE, RAMP, PULSE, NOISE, ARB, DC."""

        self.write("C{}:BSWV WVTP,{},FRQ,{},AMP,{},OFST,{},PHSE,{}", channel, type, frequency, amplitude, offset, phase)

    def sweep(self, channel=1, time=1, start=220, stop=440):
        self.write("C{}:SWWV STATE,ON,TIME,{}S,DIR,{},START,{},STOP,{},SOURCE,MAN,MTRIG",
                channel, time, "UP" if start <= stop else "DOWN", start, stop)

    def sync(self, channel=1, on=True):
        self.write("C{}:SYNC {}", channel, "ON" if on else "OFF")
