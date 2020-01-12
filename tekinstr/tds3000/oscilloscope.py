"""Oscilloscope instrument within TDS3000 Series"""
from tekinstr.oscilloscope import OscilloscopeBase, ChannelBase, ProbeBase
from tekinstr.tds3000.trigger import Trigger
from tekinstr.measurement import Measurement


class Oscilloscope(OscilloscopeBase, kind="Oscilloscope"):
    """Oscilloscope instrument within TDS3000 Series"""

    def __init__(self, instr, n_channels):
        super().__init__(instr)
        self._channels = [Channel(self, x) for x in range(1, n_channels + 1)]
        for x, ch in enumerate(self._channels, 1):
            setattr(self, f"ch{x}", ch)
        self.trigger = Trigger(self, "A")
        self.B_trigger = Trigger(self, "B")
        self.measurement = Measurement(self, 4)


class Channel(ChannelBase, kind="CH"):
    """Channel"""

    def __init__(self, owner, CHx):
        super().__init__(owner, CHx)
        self._probe = Probe(self)

    @property
    def probe(self):
        """(Probe): probe"""
        return self._probe

    def __repr__(self):
        owner = self._owner.__repr__().strip("<>")
        return f"<{owner} {self._kind}{self._ch}>"


class Probe(ProbeBase, kind="Probe"):
    """Probe"""

    @property
    def gain(self):
        """value (float): probe attenuation factor (input/output)"""
        return float(self._visa.query(f"CH{self._ch}:PROBE?"))

    def __repr__(self):
        owner = self._owner.__repr__().strip("<>")
        return f"<{owner} {self._kind} {self.model}>"
