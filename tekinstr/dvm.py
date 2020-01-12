"""Base Digital Voltmeter (DVM) definition"""
from tekinstr.common import validate
from tekinstr.instrument import Instrument


class DVMBase(Instrument, kind="DVMBase"):
    """Digital voltmeter instrument

    Attributes:
        instr (Model)
        visa (pyvisa.resources.Resource): pyvisa resource
    """

    @property
    def mode(self):
        """value (str): ACRMS, ACDCRMS, DC, Frequency or OFF"""
        return self._visa.query("DVM:MODE?")

    @mode.setter
    @validate
    def mode(self, value):
        self._visa.write(f"DVM:MODE {value}")

    @property
    def source(self):
        """value (str): CHx"""
        return self._visa.query("DVM:SOURCE?")

    @source.setter
    @validate
    def source(self, value):
        self._visa.write(f"DVM:SOURCE {value}")

    @property
    def value(self):
        """(float): measurement value"""
        return float(self._visa.query("DVM:MEASUREMENT:VALUE?"))

    @property
    def min(self):
        """(float): minimum measurement value"""
        return float(self._visa.query("DVM:MEASUREMENT:HISTORY:MINIMUM?"))

    @property
    def max(self):
        """(float): maximum measurement value"""
        return float(self._visa.query("DVM:MEASUREMENT:HISTORY:MAXIMUM?"))

    @property
    def avg(self):
        """(float): average measurement value"""
        return float(self._visa.query("DVM:MEASUREMENT:HISTORY:AVERAGE?"))

    @property
    def frequency(self):
        """(float): frequency"""
        return float(self._visa.query("DVM:MEASUREMENT:FREQUENCY?"))
