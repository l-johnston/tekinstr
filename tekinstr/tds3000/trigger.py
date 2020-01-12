"""Trigger"""
from tekinstr.instrument import InstrumentSubsystem
from tekinstr.trigger import TriggerBase, LogicInput
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
            self.pulse = PulseTrigger(self)

    def __dir__(self):
        attrs = super().__dir__()
        kind = self.kind
        if kind == "EDGE":
            attrs.remove("logic")
            attrs.remove("pulse")
        elif kind == "LOGIC":
            attrs.remove("edge")
            attrs.remove("pulse")
        else:
            attrs.remove("edge")
            attrs.remove("logic")
        return attrs


class EdgeTrigger(InstrumentSubsystem, kind="Edge"):
    """Edge trigger class

    Attributes:
        owner (Instrument)
        visa (pyvisa.resources.Resource): pyvisa resource
    """

    def __init__(self, owner):
        super().__init__(owner)
        self._designation = owner._designation

    def __repr__(self):
        instr_model = self._instr.model
        instr = self._owner._owner._kind
        subsys = self._owner._kind
        return f"<{instr_model} {instr} {self._designation}-{subsys}: {self._kind}>"

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
        """value (str): trigger on slope RISE or FALL"""
        return self._visa.query(f"TRIGGER:{self._designation}:EDGE:SLOPE?")

    @slope.setter
    @validate
    def slope(self, value):
        self._visa.write(f"TRIGGER:{self._designation}:EDGE:SLOPE {value}")

    @property
    def source(self):
        """value (str): trigger source, CHx, EXT or LINE"""
        return self._visa.query(f"TRIGGER:{self._designation}:EDGE:SOURCE?")

    @source.setter
    @validate
    def source(self, value):
        self._visa.write(f"TRIGGER:{self._designation}:EDGE:SOURCE {value}")


class LogicTrigger(InstrumentSubsystem, kind="Logic"):
    """Logic trigger class

    Attributes:
        owner (Instrument)
        visa (pyvisa.resources.Resource): pyvisa resource
    """

    def __init__(self, owner):
        super().__init__(owner)
        self._designation = "A"
        self._input_1 = LogicInput(self, 1)
        self._input_2 = LogicInput(self, 2)

    def __repr__(self):
        instr_model = self._instr.model
        instr = self._owner._owner._kind
        subsys = self._owner._kind
        return f"<{instr_model} {instr} {self._designation}-{subsys}: {self._kind}>"

    @property
    def logic_class(self):
        """value (str): trigger class, {PATTERN, STATE}"""
        return self._visa.query("TRIGGER:A:LOGIC:CLASS?")

    @logic_class.setter
    @validate
    def logic_class(self, value):
        self._visa.write(f"TRIGGER:A:LOGIC:CLASS {value}")

    @property
    def input_1(self):
        """(LogicInput): logic trigger input 1 object"""
        return self._input_1

    @property
    def input_2(self):
        """(LogicInput): logic trigger input 2 object"""
        return self._input_2

    @property
    def deltatime(self):
        """value (float): pattern trigger delta time condition"""
        q_str = f"TRIGGER:A:LOGIC:PATTERN:DELTATIME?"
        return float(self._visa.query(q_str))

    @deltatime.setter
    @validate
    def deltatime(self, value):
        cmd_str = f"TRIGGER:A:LOGIC:PATTERN:DELTATIME {value}"
        self._visa.write(cmd_str)

    @property
    def function(self):
        """value (str): logic function for pattern trigger, {AND, NAND, NOR, OR}"""
        q_str = f"TRIGGER:A:LOGIC:PATTERN:FUNCTION?"
        return self._visa.query(q_str)

    @function.setter
    @validate
    def function(self, value):
        cmd_str = f"TRIGGER:A:LOGIC:PATTERN:FUNCTION {value}"
        self._visa.write(cmd_str)

    @property
    def when_pattern(self):
        """value (str): trigger condition
            PATTERN: TRUE, FALSE, LESSTHAN, MORETHAN, EQUAL, or NOTEQUAL
        """
        q_str = f"TRIGGER:A:LOGIC:PATTERN:WHEN?"
        return self._visa.query(q_str)

    @when_pattern.setter
    @validate
    def when_pattern(self, value):
        cmd_str = f"TRIGGER:A:LOGIC:PATTERN:WHEN {value}"
        self._visa.write(cmd_str)

    @property
    def when_state(self):
        """value (str): trigger condition
            STATE: TRUE or FALSE
        """
        q_str = f"TRIGGER:A:LOGIC:STATE:WHEN?"
        return self._visa.query(q_str)

    @when_state.setter
    @validate
    def when_state(self, value):
        cmd_str = f"TRIGGER:A:LOGIC:STATE:WHEN {value}"
        self._visa.write(cmd_str)

    def __dir__(self):
        attrs = super().__dir__()
        if self.logic_class == "STATE":
            for attr in ["deltatime", "function", "when_pattern"]:
                attrs.remove(attr)
        else:
            attrs.remove("when_state")
        return attrs


class PulseTrigger(InstrumentSubsystem, kind="Pulse"):
    """Pulse trigger class

    Attributes:
        owner (Instrument)
    """

    def __init__(self, owner):
        super().__init__(owner)
        self._designation = "A"

    def __repr__(self):
        instr_model = self._instr.model
        instr = self._owner._owner._kind
        subsys = self._owner._kind
        return f"<{instr_model} {instr} {self._designation}-{subsys}: {self._kind}>"

    @property
    def pulse_class(self):
        """value (str): pulse trigger class {WIDTH, RUNT, SLEWRATE}"""
        q_str = f"TRIGGER:A:PULSE:CLASS?"
        return self._visa.query(q_str)

    @pulse_class.setter
    @validate
    def pulse_class(self, value):
        cmd_str = f"TRIGGER:A:PULSE:CLASS {value}"
        self._visa.write(cmd_str)

    @property
    def runt_polarity(self):
        """value (str): {EITHER, POSITIVE, NEGATIVE}"""
        q_str = f"TRIGGER:A:PULSE:RUNT:POLARITY?"
        return self._visa.query(q_str)

    @runt_polarity.setter
    @validate
    def runt_polarity(self, value):
        cmd_str = f"TRIGGER:A:PULSE:RUNT:POLARITY {value}"
        self._visa.write(cmd_str)

    @property
    def runt_threshold(self):
        """value (tuple or str): {(high, low), TTL, ECL}"""
        q_str = f"TRIGGER:A:PULSE:RUNT:THRESHOLD?"
        thresholds = self._visa.query(q_str).split(";")
        return tuple(float(t) for t in thresholds)

    @runt_threshold.setter
    @validate
    def runt_threshold(self, value):
        cmd_str = "TRIGGER:A:PULSE:RUNT:THRESHOLD:"
        if isinstance(value, tuple):
            high, low = value
            self._visa.write(cmd_str + f"HIGH {high}")
            self._visa.write(cmd_str + f"LOW {low}")
        else:
            self._visa.write(cmd_str + f"BOTH {value}")

    @property
    def runt_when(self):
        """value (str): {OCCURS, LESSTHAN, MOETHAN, EQUAL, NOTEQUAL}"""
        q_str = "TRIGGER:A:PULSE:RUNT:WHEN?"
        return self._visa.query(q_str)

    @runt_when.setter
    @validate
    def runt_when(self, value):
        cmd_str = f"TRIGGER:A:PULSE:RUNT:WHEN {value}"
        self._visa.write(cmd_str)

    @property
    def runt_width(self):
        """value (float): runt pulse width in seconds"""
        q_str = "TRIGGER:A:PULSE:RUNT:WIDTH?"
        return float(self._visa.query(q_str))

    @runt_width.setter
    @validate
    def runt_width(self, value):
        cmd_str = f"TRIGGER:A:PULSE:RUNT:WIDTH {value}"
        self._visa.write(cmd_str)

    @property
    def slewrate_deltatime(self):
        """value (float): slew rate trigger delta time condition"""
        q_str = f"TRIGGER:A:PULSE:SLEWRATE:DELTATIME?"
        return float(self._visa.query(q_str))

    @slewrate_deltatime.setter
    @validate
    def slewrate_deltatime(self, value):
        cmd_str = f"TRIGGER:A:PULSE:SLEWRATE:DELTATIME {value}"
        self._visa.write(cmd_str)

    @property
    def slewrate_polarity(self):
        """value (str): {EITHER, POSITIVE, NEGATIVE}"""
        q_str = f"TRIGGER:A:PULSE:SLEWRATE:POLARITY?"
        return self._visa.query(q_str)

    @slewrate_polarity.setter
    @validate
    def slewrate_polarity(self, value):
        cmd_str = f"TRIGGER:A:PULSE:SLEWRATE:POLARITY {value}"
        self._visa.write(cmd_str)

    @property
    def slewrate(self):
        """value (float): slew rate value in volts per second"""
        q_str = "TRIGGER:A:PULSE:SLEWRATE:SLEWRATE?"
        return float(self._visa.query(q_str))

    @slewrate.setter
    def slewrate(self, value):
        cmd_str = f"TRIGGER:A:PULSE:SLEWRATE:SLEWRATE {value}"
        self._visa.write(cmd_str)

    @property
    def slewrate_threshold(self):
        """value (tuple or str): {(high, low), TTL, ECL}"""
        q_str = f"TRIGGER:A:PULSE:SLEWRATE:THRESHOLD?"
        thresholds = self._visa.query(q_str).split(";")
        return tuple(float(t) for t in thresholds)

    @slewrate_threshold.setter
    @validate
    def slewrate_threshold(self, value):
        cmd_str = "TRIGGER:A:PULSE:SLEWRATE:THRESHOLD:"
        if isinstance(value, tuple):
            high, low = value
            self._visa.write(cmd_str + f"HIGH {high}")
            self._visa.write(cmd_str + f"LOW {low}")
        else:
            self._visa.write(cmd_str + f"BOTH {value}")

    @property
    def slewrate_when(self):
        """value (str): {OCCURS, LESSTHAN, MOETHAN, EQUAL, NOTEQUAL}"""
        q_str = "TRIGGER:A:PULSE:SLEWRATE:WHEN?"
        return self._visa.query(q_str)

    @slewrate_when.setter
    @validate
    def slewrate_when(self, value):
        cmd_str = f"TRIGGER:A:PULSE:SLEWRATE:WHEN {value}"
        self._visa.write(cmd_str)

    @property
    def width_polarity(self):
        """value (str): {POSITIVE, NEGATIVE}"""
        q_str = f"TRIGGER:A:PULSE:WIDTH:POLARITY?"
        return self._visa.query(q_str)

    @width_polarity.setter
    @validate
    def width_polarity(self, value):
        cmd_str = f"TRIGGER:A:PULSE:WIDTH:POLARITY {value}"
        self._visa.write(cmd_str)

    @property
    def width_when(self):
        """value (str): {LESSTHAN, MOETHAN, EQUAL, NOTEQUAL}"""
        q_str = "TRIGGER:A:PULSE:WIDTH:WHEN?"
        return self._visa.query(q_str)

    @width_when.setter
    @validate
    def width_when(self, value):
        cmd_str = f"TRIGGER:A:PULSE:WIDTH:WHEN {value}"
        self._visa.write(cmd_str)

    @property
    def pulse_width(self):
        """value (float): pulse width trigger time period in seconds"""
        q_str = "TRIGGER:A:PULSE:WIDTH:WIDTH?"
        return float(self._visa.query(q_str))

    @pulse_width.setter
    @validate
    def pulse_width(self, value):
        cmd_str = f"TRIGGER:A:PULSE:WIDTH:WIDTH {value}"
        self._visa.write(cmd_str)

    def __dir__(self):
        attrs = super().__dir__()
        width_attrs = ["width_polarity", "width_when", "pulse_width"]
        runt_attrs = ["runt_polarity", "runt_threshold", "runt_when", "runt_width"]
        slewrate_attrs = [
            "slewrate_deltatime",
            "slewrate_polarity",
            "slewrate",
            "slewrate_threshold",
            "slewrate_when",
        ]
        pulse_class = self.pulse_class
        if pulse_class == "WIDTH":
            for attr in runt_attrs + slewrate_attrs:
                attrs.remove(attr)
        elif pulse_class == "RUNT":
            for attr in width_attrs + slewrate_attrs:
                attrs.remove(attr)
        else:
            for attr in width_attrs + runt_attrs:
                attrs.remove(attr)
        return attrs
