import usbtmc

import logging
logger = logging.getLogger(__name__)


class Instrument:
    usbid = None

    def __init__(self):
        assert self.usbid
        self.instrument = usbtmc.Instrument(*self.usbid)
        self.name = self.idn()

    def unlock(self):
        self.instrument.unlock()

    def idn(self):
        return self.ask("*IDN?")

    def reset(self):
        return self.write("*RST")

    def write(self, cmd, *args, **kwargs):
        line = cmd.format(*args, **kwargs)
        logger.debug("{}: {}".format(self.__class__.__name__, line))
        self.instrument.write(line)

    def ask(self, cmd, *args, **kwargs):
        line = cmd.format(*args, **kwargs)
        ret = self.instrument.ask(line)
        logger.debug("{}: {} => {}".format(self.__class__.__name__, line, ret))
        return ret
