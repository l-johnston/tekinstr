"""Trigger definitions"""
from tekinstr.instrument import InstrumentSubsystem
from tekinstr.trigger import TriggerBase
from tekinstr.common import validate


class Trigger(TriggerBase, kind="Trigger"):
    """Trigger class

    Attributes:
        owner (Instrument)
        visa (pyvisa.resources.Resource): pyvisa resource
        designation (str): A or B
    """

    def __init__(self, owner, designation):
        super().__init__(owner, designation)
        self.edge = EdgeTrigger(self)
        if designation == "A":
            self.logic = LogicTrigger(self)

    def __dir__(self):
        attrs = super().__dir__()
        if self.kind == "EDGE":
            attrs.remove("logic")
        else:
            attrs.remove("edge")
        return attrs


class EdgeTrigger(InstrumentSubsystem, kind="Edge"):
    """Edge trigger class

    Attributes:
        owner (Instrument)
    """

    def __init__(self, owner):
        super().__init__(owner)
        self._designation = owner._designation

    @property
    def coupling(self):
        """value (str): {AC, DC, HFRej, LFRej, NOISErej}"""
        return self._visa.query(f"TRIGGER:{self._designation}:EDGE:COUPLING?")

    @coupling.setter
    @validate
    def coupling(self, value):
        self._visa.write(f"TRIGGER:{self._designation}:EDGE:COUPLING {value}")

    @property
    def slope(self):
        """value (str): trigger on slope, {RISE, FALL, EITHER}"""
        return self._visa.query(f"TRIGGER:{self._designation}:EDGE:SLOPE?")

    @slope.setter
    @validate
    def slope(self, value):
        self._visa.write(f"TRIGGER:{self._designation}:EDGE:SLOPE {value}")

    @property
    def source(self):
        """value (str): trigger source, {AUX, CHx, Dx, LINE, RF}"""
        return self._visa.query(f"TRIGGER:{self._designation}:EDGE:SOURCE?")

    @source.setter
    @validate
    def source(self, value):
        self._visa.write(f"TRIGGER:{self._designation}:EDGE:SOURCE {value}")


class LogicTrigger(InstrumentSubsystem, kind="Logic"):
    """Logic trigger class

    Attributes:
        owner (Instrument)
    """

    def __init__(self, owner):
        super().__init__(owner)
        self._designation = "A"
        n_channels = self._instr.features["ANALOG:NUMCHANNELS"]
        self._channels = [LogicInputChannel(self, n) for n in range(1, n_channels + 1)]
        for x, ch in enumerate(self._channels, 1):
            setattr(self, f"ch{x}", ch)
        self.clock = LogicClock(self)
        self.pattern = LogicPattern(self)

    @property
    def function(self):
        """value (str): {AND, NAND, NOR, OR}"""
        q_str = f"TRIGGER:A:LOGIC:FUNCTION?"
        return self._visa.query(q_str)

    @function.setter
    @validate
    def function(self, value):
        cmd_str = f"TRIGGER:A:LOGIC:FUNCTION {value}"
        self._visa.write(cmd_str)

    def __dir__(self):
        attrs = super().__dir__()
        if self.clock.source is not None:
            attrs.remove("pattern")
        return attrs


class LogicInputChannel(InstrumentSubsystem, kind="LogicInput"):
    """Logic input channel state and threshold

    Attributes:
        owner (Instrument)
        visa (pyvisa.resources.Resource): pyvisa resource
        CHx (int): input channel
    """

    def __init__(self, owner, CHx):
        super().__init__(owner)
        self._designation = "A"
        self._ch = CHx

    def __repr__(self):
        return f"<{self._designation} trigger: {self._kind}>"

    @property
    def state(self):
        """value (str): input condition, {HIGH, LOW, X}"""
        q_str = f"TRIGGER:A:LOGIC:INPUT:CH{self._ch}?"
        return self._visa.query(q_str)

    @state.setter
    @validate
    def state(self, value):
        cmd_str = f"TRIGGER:A:LOGIC:INPUT:CH{self._ch} {value}"
        self._visa.write(cmd_str)

    @property
    def threshold(self):
        """value (float or str): {voltage, ECL, TTL}"""
        q_str = f"TRIGGER:A:LOGIC:THRESHOLD:CH{self._ch}?"
        value = self._visa.query(q_str)
        try:
            value = float(value)
        except ValueError:
            pass
        return value

    @threshold.setter
    @validate
    def threshold(self, value):
        cmd_str = f"TRIGGER:A:LOGIC:THRESHOLD:CH{self._ch} {value}"
        self._visa.write(cmd_str)


class LogicClock(InstrumentSubsystem, kind="LogicClock"):
    """Logic clock source and edge

    Attributes:
        owner (Instrument)
    """

    def __init__(self, owner):
        super().__init__(owner)
        self._designation = "A"

    def __repr__(self):
        return f"<{self._designation} trigger: {self._kind}>"

    @property
    def source(self):
        """value (str): clock source, {CHx, Dx, RF, NONE}"""
        q_str = "TRIGGER:A:LOGIC:INPUT:CLOCK:SOURCE?"
        value = self._visa.query(q_str)
        return None if value == "NONE" else value

    @source.setter
    @validate
    def source(self, value):
        cmd_str = f"TRIGGER:A:LOGIC:INPUT:CLOCK:SOURCE {value}"
        self._visa.write(cmd_str)

    @property
    def edge(self):
        """value (str): {RISE, FALL}"""
        q_str = "TRIGGER:A:LOGIC:INPUT:CLOCK:EDGE?"
        return self._visa.query(q_str)

    @edge.setter
    @validate
    def edge(self, value):
        cmd_str = f"TRIGGER:A:LOGIC:INPUT:CLOCK:EDGE {value}"
        self._visa.write(cmd_str)


class LogicPattern(InstrumentSubsystem, kind="Logic Pattern"):
    """Logic pattern

    Attributes:
        owner (Instrument)
    """

    @property
    def when(self):
        """value (str): {TRUE, FALSE, LESSTHAN, MORETHAN, EQUAL, UNEQUAL}"""
        q_str = "TRIGGER:A:LOGIC:PATTERN:WHEN?"
        return self._visa.query(q_str)

    @when.setter
    @validate
    def when(self, value):
        cmd_str = f"TRIGGER:A:LOGIC:PATTERN:WHEN {value}"
        self._visa.write(cmd_str)

    @property
    def deltatime(self):
        """value (float): trigger delta time in seconds"""
        q_str = "TRIGGER:A:LOGIC:PATTERN:DELTATIME?"
        return float(self._visa.query(q_str))

    @deltatime.setter
    @validate
    def deltatime(self, value):
        cmd_str = f"TRIGGER:A:LOGIC:PATTERN:DELTATIME {value}"
        self._visa.write(cmd_str)


class SetHoldTrigger(InstrumentSubsystem, kind="SetHold"):
    """Logic setup & hold trigger class

    Attributes:
        owner (Instrument)
    """

    def __init__(self, owner):
        super().__init__(owner)
        self._designation = "A"

    def __repr__(self):
        return f"<{self._designation} trigger: {self._kind}>"
