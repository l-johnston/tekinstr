"""Instrument base class"""
from tekinstr.common import TekBase


class Instrument(TekBase):
    """Base class for a specific type of instrument within a given model

    Attributes:
        instr (Model)
    """

    _kind = "Instrument"

    def __init__(self, instr):
        super().__init__(instr._visa)
        self._instr = instr

    def __init_subclass__(cls, kind):
        cls._kind = kind

    def __get__(self, instance, owner=None):
        return self

    def __repr__(self):
        return f"<{self._instr.model} {self._kind}>"


class InstrumentSubsystem(Instrument, kind="InstrumentSubsystem"):
    """Base class for an instrument subsystem

    Attributes:
        owner (Instrument)
    """

    def __init__(self, owner):
        super().__init__(owner._instr)
        self._owner = owner

    def __repr__(self):
        return f"<{self._instr.model} {self._owner._kind} {self._kind}>"
