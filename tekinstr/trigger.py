"""Trigger base definitions"""
from tekinstr.instrument import InstrumentSubsystem
from tekinstr.common import validate


class TriggerBase(InstrumentSubsystem, kind="TriggerBase"):
    """Trigger base class for all trigger types

    Attributes:
        owner (Instrument)
        designation (str): A or B
    """

    def __init__(self, owner, designation):
        super().__init__(owner)
        self._designation = designation

    def __repr__(self):
        return f"<{self._instr.model} {self._owner._kind} {self._designation}-{self._kind}>"

    @property
    def kind(self):
        """value (str): type of trigger; {EDGE, LOGIC, PULSE}"""
        return self._visa.query(f"TRIGGER:{self._designation}:TYPE?")

    @kind.setter
    @validate
    def kind(self, value):
        if self._designation == "B":
            raise AttributeError("can't set B trigger type")
        self._visa.write(f"TRIGGER:{self._designation}:TYPE {value}")

    @property
    def parameters(self):
        """(dict): trigger parameters"""
        return self._get_parameters()

    def _get_parameters(self):
        self._visa.write("HEADER ON")
        raw_str = self._visa.query(f"TRIGGER:{self._designation}?")
        self._visa.write("HEADER OFF")
        parameters = dict([p.split(" ", maxsplit=1) for p in raw_str.split(";")])
        for k, v in parameters.items():
            try:
                v = int(v)
            except ValueError:
                try:
                    v = float(v)
                except ValueError:
                    pass
            parameters[k] = v
        return parameters

    @property
    def mode(self):
        """value (str): A trigger mode, AUTO or NORMAL"""
        return self._visa.query("TRIGGER:A:MODE?")

    @mode.setter
    @validate
    def mode(self, value):
        self._visa.write(f"TRIGGER:A:MODE {value}")

    @property
    def state(self):
        """value (str): B trigger state, ON or OFF"""
        return self._visa.query("TRIGGER:B:STATE?")

    @state.setter
    @validate
    def state(self, value):
        self._visa.write(f"TRIGGER:B:STATE {value}")

    @property
    def level(self):
        """value (float or str): trigger threshold level, {voltage, ECL, TTL}
            float: level in volts
            str: ECL (-1.3 V) or TTL (1.4 V)
        """
        level = self._visa.query(f"TRIGGER:{self._designation}:LEVEL?")
        try:
            level = float(level)
        except ValueError:
            pass
        return level

    @level.setter
    @validate
    def level(self, value):
        self._visa.write(f"TRIGGER:{self._designation}:LEVEL {value}")

    def set_level(self):
        """set trigger level to 50 %"""
        self._visa.write(f"TRIGGER:{self._designation}:SETLEVEL")

    @property
    def by(self):
        """value (str): delay B trigger by TIME or EVENTS"""
        return self._visa.query("TRIGGER:B:BY?")

    @by.setter
    @validate
    def by(self, value):
        self._visa.write(f"TRIGGER:B:BY {value}")

    @property
    def time(self):
        """value (float): delay B trigger by value seconds when 'by' set to TIME"""
        return float(self._visa.query("TRIGGER:B:TIME?"))

    @time.setter
    @validate
    def time(self, value):
        self._visa.write(f"TRIGGER:B:TIME {value}")

    @property
    def events(self):
        """value (int): B trigger occurs on the value occurance after A trigger"""
        return int(self._visa.query("TRIGGER:B:EVENTS?"))

    @events.setter
    @validate
    def events(self, value):
        self._visa.write(f"TRIGGER:B:EVENTS:COUNT {value}")

    @property
    def holdoff(self):
        """value (float): A trigger holdoff time in seconds"""
        return float(self._visa.query("TRIGGER:A:HOLDOFF?"))

    @holdoff.setter
    @validate
    def holdoff(self, value):
        self._visa.write(f"TRIGGER:A:HOLDOFF:TIME {value}")

    def __dir__(self):
        attrs = super().__dir__()
        if self._designation == "A":
            for attr in ["state", "by", "time", "events"]:
                attrs.remove(attr)
        else:
            for attr in ["mode", "holdoff"]:
                attrs.remove(attr)
        return sorted(attrs)


class LogicInput(InstrumentSubsystem, kind="LogicTrigger:Input"):
    """Logic Input class

    Attributes:
        owner (LogicTrigger)
        input_n (int): logic trigger input, 1 or 2
    """

    def __init__(self, owner, input_n):
        super().__init__(owner)
        self._input_n = input_n

    def __repr__(self):
        instr_model = self._instr.model
        instr = self._owner._owner._kind
        subsys = self._owner._kind
        return f"<{instr_model} {instr} {subsys} {self._kind}>"

    @property
    def level(self):
        """value (str): HIGH or LOW"""
        q_str = f"TRIGGER:A:LOGIC:INPUT{self._input_n}:LOGICLEVEL?"
        return self._visa.query(q_str)

    @level.setter
    @validate
    def level(self, value):
        cmd_str = f"TRIGGER:A:LOGIC:INPUT{self._input_n}:LOGICLEVEL {value}"
        self._visa.write(cmd_str)

    @property
    def slope(self):
        """value (str): input 2 state logic trigger slope, RISE or FALL"""
        q_str = f"TRIGGER:A:LOGIC:INPUT2:SLOPE?"
        return self._visa.query(q_str)

    @slope.setter
    @validate
    def slope(self, value):
        cmd_str = f"TRIGGER:A:LOGIC:INPUT2:SLOPE {value}"
        self._visa.write(cmd_str)

    def __dir__(self):
        attrs = super().__dir__()
        if self._input_n == 1:
            attrs.remove("slope")
        return attrs

    @property
    def source(self):
        """value (str): input signal source, CHx"""
        q_str = f"TRIGGER:A:LOGIC:INPUT{self._input_n}:SOURCE?"
        return self._visa.query(q_str)

    @source.setter
    @validate
    def source(self, value):
        cmd_str = f"TRIGGER:A:LOGIC:INPUT{self._input_n}:SOURCE {value}"
        self._visa.write(cmd_str)

    @property
    def threshold(self):
        """value (float or str): threshold in volts, ECL or TTL"""
        q_str = f"TRIGGER:A:LOGIC:INPUT{self._input_n}:THRESHOLD?"
        threshold_str = self._visa.query(q_str)
        try:
            threshold = float(threshold_str)
        except ValueError:
            threshold = threshold_str
        return threshold

    @threshold.setter
    @validate
    def threshold(self, value):
        cmd_str = f"TRIGGER:A:LOGIC:INPUT{self._input_n}:THRESHOLD {value}"
        self._visa.write(cmd_str)
