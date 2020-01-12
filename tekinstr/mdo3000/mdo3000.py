"""MDO3000 Series Oscilloscope"""
import re
from tekinstr.model import Model
from tekinstr.mdo3000.oscilloscope import Oscilloscope
from tekinstr.mdo3000.dvm import DVM
from tekinstr.mdo3000.spectrum_analyzer import SpectrumAnalyzer
from tekinstr.common import validate


class MDO3000(Model):
    """MDO3000 Series Oscilloscope class

    Attributes:
        resource (pyvisa.resources.Resource): pyvisa resource
    """

    def __init__(self, visa):
        super().__init__(visa)
        features = self._get_configuration()
        n_channels = features["ANALOG:NUMCHANNELS"]
        self.oscilloscope = Oscilloscope(self, n_channels)
        if features["DVM"]:
            self.dvm = DVM(self)
        if features["RF:NUMCHANNELS"] > 0:
            self.spectrum_analyzer = SpectrumAnalyzer(self)
        self._display = self._get_select()[0]

    @property
    def features(self):
        """(dict): model features"""
        return self._get_configuration()

    def _get_configuration(self):
        """Get the instrument configuration"""
        bool_features = [
            "ADVMATH",
            "AFG",
            "APPLICATIONS:POWER",
            "ARB",
            "AUXIN",
            "DVM",
        ]
        int_features = [
            "ANALOG:NUMCHANNELS",
            "DIGITAL:NUMCHANNELS",
            "NUMMEAS",
            "RF:NUMCHANNELS",
        ]
        configuration = {}
        for feature in bool_features:
            value = bool(int(self._visa.query(f"CONFIGURATION:{feature}?")))
            configuration[feature] = value
        for feature in int_features:
            value = int(self._visa.query(f"CONFIGURATION:{feature}?"))
            configuration[feature] = value
        return configuration

    def _get_select(self):
        """Get the current display selection"""
        original_header_state = self._visa.query("HEADER?")
        self._visa.write("HEADER ON")
        select_str = self._visa.query("SELECT?").replace(":SELECT:", "")
        raw_select = dict([kv.split(" ", maxsplit=1) for kv in select_str.split(";")])
        displayed_channels = set()
        control_channel = raw_select.pop("CONTROL", None)
        for k, v in raw_select.items():
            if v in ["1", "ON"]:
                k = "RF" if k.startswith("RF") else k
                displayed_channels.add(k)
        self._visa.write(f"HEADER {original_header_state}")
        return (displayed_channels, control_channel)

    @property
    def display(self):
        """channel(s) (str, list): display the given channel(s);
            'CHx', 'CHx:y', ['CHx', 'CHy'], or 'RF'
            The oscilloscope and spectrum analyzer are mutually exclusive systems and
            cannot be displayed simultaneously.
        """
        self._display = self._get_select()[0]
        return self._display

    @display.setter
    @validate
    def display(self, channels):
        chs = []
        if isinstance(channels, str) and channels.startswith("CH"):
            match = re.match("^CH(?P<first>[1-4])(?P<last>:[1-4])?$", channels)
            if match is None:
                raise ValueError(f"{channels} not a valid specification")
            first = int(match.group("first"))
            last = match.group("last")
            if last is None:
                last = first
            else:
                last = int(last[-1])
            for ch in range(first, last + 1):
                chs.append(f"CH{ch}")
            channels = chs
        elif isinstance(channels, str) and channels.startswith("RF"):
            channels = ["RF_NORMAL"]
        channels = set(channels)
        displayed_channels = self.display
        for channel in displayed_channels - channels:
            self._visa.write(f"SELECT:{channel} OFF")
        for channel in channels - displayed_channels:
            self._visa.write(f"SELECT:{channel} ON")
        self._display = self._get_select()[0]
