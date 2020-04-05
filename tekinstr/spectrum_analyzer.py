"""Base Spectrum Analyzer definition"""
import re
from datetime import datetime
import numpy as np
from tekinstr.common import validate
from tekinstr.instrument import Instrument
from waveformDT.waveform import WaveformDT


class SpectrumAnalyzerBase(Instrument, kind="Base Spectrum Analyzer"):
    """Spectrum analyzer instrument

    Attributes:
        instr (Model)
        visa (pyvisa.resources.Resource): pyvisa resource
    """

    def _get_wfmpre(self, inout=""):
        self._visa.write("HEADER ON")
        pre_str = self._visa.query(f"WFM{inout}PRE?").replace(f":WFM{inout}PRE:", "")
        raw_preamble = dict([kv.split(" ", maxsplit=1) for kv in pre_str.split(";")])
        preamble = {}
        for k, v in raw_preamble.items():
            value = v.strip('"')
            try:
                value = int(v)
            except ValueError:
                try:
                    value = float(v)
                except ValueError:
                    pass
            preamble[k] = value
        self._visa.write("HEADER OFF")
        return preamble

    def _get_select(self):
        """Get the current display selection"""
        self._visa.write("HEADER ON")
        select_str = self._visa.query("SELECT?").replace(":SELECT:", "")
        raw_select = dict([kv.split(" ", maxsplit=1) for kv in select_str.split(";")])
        displayed_channels = set()
        control_channel = raw_select.pop("CONTROL", None)
        for k, v in raw_select.items():
            if k.startswith("RF") and v in ["1", "ON"]:
                k = k.split("RF_")[1].replace("MIN", "MIN ").replace("MAX", "MAX ")
                displayed_channels.add(k)
        self._visa.write("HEADER OFF")
        return (displayed_channels, control_channel)

    @property
    def trace(self):
        """value (str): displayed spectrum trace; normal, average, min hold, max hold"""
        return self._get_select()[0]

    @trace.setter
    @validate
    def trace(self, value):
        raw_traces = [value] if isinstance(value, str) else value
        traces = set()
        for raw_tr in raw_traces:
            tr = raw_tr.upper().replace("MIN ", "MIN").replace("MAX ", "MAX")
            traces.add(tr)
        displayed_traces = self.trace
        for tr in displayed_traces - traces:
            self._visa.write(f"SELECT:RF_{tr} OFF")
        for tr in traces - displayed_traces:
            self._visa.write(f"SELECT:RF_{tr} ON")

    @property
    def center_frequency(self):
        """value (float): center frequency in hertz"""
        return float(self._visa.query("RF:FREQUENCY?"))

    @center_frequency.setter
    @validate
    def center_frequency(self, value):
        self._visa.write(f"RF:FREQUENCY {float(value)}")

    @property
    def span(self):
        """value (float): span"""
        return float(self._visa.query("RF:SPAN?"))

    @span.setter
    @validate
    def span(self, value):
        self._visa.write(f"RF:SPAN {float(value)}")

    @property
    def rbw_mode(self):
        """value (str): resolution bandwidth (rbw) mode; AUTO or MANUAL"""
        return self._visa.query("RF:RBW:MODE?")

    @rbw_mode.setter
    @validate
    def rbw_mode(self, value):
        self._visa.write(f"RF:RBW:MODE {value}")

    @property
    def rbw(self):
        """value (float): resolution bandwidth"""
        return float(self._visa.query("RF:RBW?"))

    @rbw.setter
    @validate
    def rbw(self, value):
        self._visa.write(f"RF:RBW {value}")

    @property
    def rbw_ratio(self):
        """value (float): ration of span to resolution bandwidth"""
        return float(self._visa.query("RF:SPANRBWRATIO?"))

    @rbw_ratio.setter
    @validate
    def rbw_ratio(self, value):
        self._visa.write(f"RF:SPANRBWRATIO {float(value)}")

    @property
    def ref_level(self):
        """value (float): reference level"""
        return float(self._visa.query("RF:REFLEVEL?"))

    @ref_level.setter
    @validate
    def ref_level(self, value):
        self._visa.write(f"RF:REFLEVEL {value}")

    @property
    def vertical_position(self):
        """value (float): vertical position"""
        return float(self._visa.query("RF:POSITION?"))

    @vertical_position.setter
    @validate
    def vertical_position(self, value):
        self._visa.write(f"RF:POSITION {float(value)}")

    @property
    def vertical_scale(self):
        """value (float): vertical_unit per division"""
        return float(self._visa.query("RF:SCALE?"))

    @vertical_scale.setter
    @validate
    def vertical_scale(self, value):
        self._visa.write(f"RF:SCALE {float(value)}")

    @property
    def vertical_unit(self):
        """value (str): vertical unit; dBm, dBuw, etc."""
        return self._visa.query("RF:UNITS?")

    @vertical_unit.setter
    @validate
    def vertical_unit(self, value):
        self._visa.write(f"RF:UNITS {value}")

    @property
    def window(self):
        """value (str): window function"""
        return self._visa.query("RF:WINDOW?")

    @window.setter
    @validate
    def window(self, value):
        self._visa.write(f"RF:WINDOW {value}")

    @property
    def label(self):
        """value (str): label"""
        return self._visa.query("RF:LABEL?").strip('"')

    @label.setter
    @validate
    def label(self, value):
        self._visa.write(f"RF:LABEL '{value}'")

    def read(self, dB=True, wdt=True):
        """Transfer RF spectrum

        Args:
            dB (bool): scale data in dB if True, otherwise unit is watts
            wdt (bool): return data as WaveformDT, otherwise Numpy ndarray
        Returns:
            (ndarray or WaveformDT)
        """
        self._visa.write("DATA:SOURCE RF_NORMAL")
        preamble = self._get_wfmpre("OUT")
        time = self._visa.query("TIME?")
        date = self._visa.query("DATE?")
        data = self._visa.query_binary_values(
            "CURVE?", is_big_endian=True, container=np.ndarray
        )
        if dB:
            match = re.match("^DB(?P<prefix>[UM])(?P<unit>[AVW])*$", self.vertical_unit)
            prefix = "m" if match.group("prefix") == "M" else "µ"
            unit = "W" if match.group("unit") is None else match.group("unit")
            y_unit = "dB" + prefix + unit
            scale = 10 if unit == "W" else 20
            ref = 1e-3 if prefix == "m" else 1e-6
            data = scale * np.log10(data / ref)
        else:
            y_unit = "W"
        if wdt:
            time = [int(n) for n in time.strip().strip('"').split(":")]
            date = [int(n) for n in date.strip().strip('"').split("-")]
            t0 = datetime(*date, *time)
            dt = preamble["XINCR"]
            data = WaveformDT(data, dt, t0)
            setattr(data, "wf_start_offset", preamble["XZERO"])
            setattr(data, "x_unit", preamble["XUNIT"])
            setattr(data, "y_unit", y_unit)
        return data

    @property
    def clipping(self):
        """(bool): RF input clipping"""
        value = self._visa.query("RF:CLIPPING?")
        return value in ["1", "ON"]
