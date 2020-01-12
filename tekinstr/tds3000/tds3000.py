"""TDS3000 Series Oscilloscope"""
import re
from tekinstr.model import Model
from tekinstr.tds3000.oscilloscope import Oscilloscope


class TDS3000(Model):
    """TDS3000 Series Oscilloscope class

    Attributes:
        resource (pyvisa.resources.Resource): pyvisa resource
    """

    def __init__(self, visa):
        super().__init__(visa)
        self._visa.timeout = 4000
        pattern = "^TDS30(?P<full_bw>[1-6])(?P<n_channels>[24])[BC]*$"
        match = re.match(pattern, self.model)
        n_channels = int(match.group("n_channels"))
        self._full_bw = f"{match.group('full_bw')}00 MHz"
        self.oscilloscope = Oscilloscope(self, n_channels)

    @property
    def full_bandwidth(self):
        """(str): analog bandwidth when bandwidth is set to FULL"""
        return self._full_bw

    @property
    def battery_soc(self):
        """(float): percent battery state of charge"""
        soc = 100 * int(self._visa.query("POWER:BATTERY:GASGAUGE?")) / 15
        return soc
