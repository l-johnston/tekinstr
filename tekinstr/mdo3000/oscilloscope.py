"""Oscilloscope instrument definition"""
from tekinstr.common import validate
from tekinstr.oscilloscope import OscilloscopeBase, ChannelBase, ProbeBase
from tekinstr.mdo3000.trigger import Trigger
from tekinstr.measurement import Measurement


class Oscilloscope(OscilloscopeBase, kind="Oscilloscope"):
    """Oscilloscope instrument

    Attributes:
        instr (Model)
        n_channels (int): number of channels
    """

    def __init__(self, instr, n_channels):
        super().__init__(instr)
        self._channels = [Channel(self, x) for x in range(1, n_channels + 1)]
        for x, ch in enumerate(self._channels, 1):
            setattr(self, f"ch{x}", ch)
        self.trigger = Trigger(self, "A")
        self.measurement = Measurement(self, 4)

    @property
    def sample_rate(self):
        """(float): sample rate in hertz
            The oscilloscope always acquires at this maximum rate and the displayed
            waveform is decimated according to the time per division setting.
        """
        return float(self._visa.query("HORIZONTAL:SAMPLERATE?"))

    @property
    def record_length(self):
        """value (int): 1e3, 1e4, 1e5, 1e6, 5e6, 1e7 samples"""
        return int(self._visa.query("HORIZONTAL:RECORDLENGTH?"))

    @record_length.setter
    def record_length(self, value):
        self._visa.write(f"HORIZONTAL:RECORDLENGTH {int(value)}")

    @property
    def horizontal_delay_mode(self):
        """value (str): delay_time or pretrigger_percent
            delay_time: center waveform horizontal_position seconds after trigger occurs
            pretrigger_percent: horizontal_position percent of record length
        """
        mode = self._visa.query("HORIZONTAL:DELAY:MODE?")
        return "delay_time" if mode in ["ON", "1"] else "pretrigger_percent"

    @horizontal_delay_mode.setter
    @validate
    def horizontal_delay_mode(self, value):
        mode = "ON" if value == "delay_time" else "OFF"
        self._visa.write(f"HORIZONTAL:DELAY:MODE {mode}")

    @property
    def horizontal_position(self):
        """value (float): position of waveform on display based on horizontal_delay_mode
            delay_time: center waveform horizontal_position seconds after trigger occurs
            pretrigger_percent: horizontal_position percent of record length
        """
        delay_time = float(self._visa.query("HORIZONTAL:DELAY:TIME?"))
        pretrigger_percent = float(self._visa.query("HORIZONTAL:POSITION?"))
        if self.horizontal_delay_mode in ["0", "OFF"]:
            horizontal_position = pretrigger_percent
        else:
            horizontal_position = delay_time
        return horizontal_position

    @horizontal_position.setter
    @validate
    def horizontal_position(self, value):
        if self.horizontal_delay_mode in ["0", "OFF"]:
            self._visa.write(f"HORIZONTAL:POSITION {value}")
        else:
            self._visa.write(f"HORIZONTAL:DELAY:TIME {value}")

    @property
    def acquisition_mode(self):
        """value (str): SAMPLE, PEAKDETECT, HIRES, AVERAGE, ENVELOPE
            AVERAGE - specify num_averages
            ENVELOPE - specify num_envelopes
        """
        return self._visa.query("ACQUIRE:MODE?")

    @acquisition_mode.setter
    @validate
    def acquisition_mode(self, value):
        self._visa.write(f"ACQUIRE:MODE {value}")

    def _get_wfmpre(self, inout=""):
        return super()._get_wfmpre("OUT")


class Channel(ChannelBase, kind="CH"):
    """Oscilloscope channel

    Attributes:
        owner (Instrument)
        CHx (int): channel number
    """

    def __init__(self, owner, CHx):
        super().__init__(owner, CHx)
        self._probe = Probe(self)

    @property
    def probe(self):
        """(Probe): probe"""
        return self._probe

    @property
    def label(self):
        """label (str): channel label"""
        return self._visa.query(f"CH{self._ch}:LABEL?").strip('"')

    @label.setter
    @validate
    def label(self, value):
        self._visa.write(f"CH{self._ch}:LABEL '{value}'")

    @property
    def coupling(self):
        """value (str): channel coupling AC or DC"""
        return self._visa.query(f"CH{self._ch}:COUPLING?")

    @coupling.setter
    @validate
    def coupling(self, value):
        self._visa.write(f"CH{self._ch}:COUPLING {value}")

    @property
    def termination(self):
        """value (float): channel termination in ohms, (1e6, 50, 75) Ω"""
        return float(self._visa.query(f"CH{self._ch}:TER?"))

    @termination.setter
    @validate
    def termination(self, value):
        self._visa.write(f"CH{self._ch}:TER {float(value)}")

    @property
    def bandwidth(self):
        """value (float or str): float hertz or FULL"""
        bandwidth = self._visa.query(f"CH{self._ch}:BANDWIDTH?")
        try:
            bandwidth = float(bandwidth)
        except ValueError:
            pass
        return bandwidth

    @bandwidth.setter
    @validate
    def bandwidth(self, value):
        try:
            bandwidth = float(value)
        except ValueError:
            bandwidth = value
        self._visa.write(f"CH{self._ch}:BANDWIDTH {bandwidth}")

    @property
    def trigger_level(self):
        """value (float or str): A-trigger threshold level, {voltage, ECL, TTL}
            float: level in volts
            str: ECL (-1.3 V) or TTL (1.4 V)
        """
        level = self._visa.query(f"TRIGGER:A:LEVEL:CH{self._ch}?")
        try:
            level = float(level)
        except ValueError:
            pass
        return level

    @trigger_level.setter
    @validate
    def trigger_level(self, value):
        self._visa.write(f"TRIGGER:A:LEVEL:CH{self._ch} {value}")

    @property
    def logic_input(self):
        """value (str): input condition for logic triggering, {HIGH, LOW, X}"""
        q_str = f"TRIGGER:A:LOGIC:INPUT:CH{self._ch}?"
        return self._visa.query(q_str)

    @logic_input.setter
    @validate
    def logic_input(self, value):
        cmd_str = f"TRIGGER:A:LOGIC:INPUT:CH{self._ch} {value}"
        self._visa.write(cmd_str)

    @property
    def logic_threshold(self):
        """value (float or str): A-trigger logic threshold, {voltage, ECL, TTL}"""
        q_str = f"TRIGGER:A:LOGIC:THRESHOLD:CH{self._ch}?"
        threshold = self._visa.query(q_str)
        try:
            threshold = float(threshold)
        except ValueError:
            pass
        return threshold

    @logic_threshold.setter
    @validate
    def logic_threshold(self, value):
        cmd_str = f"TRIGGER:A:LOGIC:THRESHOLD:CH{self._ch} {value}"
        self._visa.write(cmd_str)


class MeasurementSlot:
    """Automated measurement system of the oscilloscope

    Attributes:
        slot (int): measurement slot; 1 to 4
        resource (pyvisa.resources.Resource): pyvisa resource
    """

    def __init__(self, slot, resource):
        self._slot = slot
        self._source = "CH1"
        self._type = "amplitude"
        self._visa = resource
        self._visa.write(f"MEASUREMENT:MEAS{self._slot}:SOURCE1 {self._source}")
        self._visa.write(f"MEASUREMENT:MEAS{self._slot}:TYPE {self._type}")
        self._state = "OFF"
        self._visa.write(f"MEASUREMENT:MEAS{self._slot}:STATE {self._state}")

    @property
    def source(self):
        """value (str): source channel; CHx, x in 1 to 4"""
        self._source = self._visa.query(f"MEASUREMENT:MEAS{self._slot}:SOURCE?")
        return self._source

    @source.setter
    @validate
    def source(self, value):
        self._visa.write(f"MEASUREMENT:MEAS{self._slot}:SOURCE {value}")
        self._source = self._visa.query(f"MEASUREMENT:MEAS{self._slot}:SOURCE?")

    @property
    def measurement_type(self):
        """value (str): measurement type; amplitude, frequency, etc."""
        self._type = self._visa.query(f"MEASUREMENT:MEAS{self._slot}:TYPE?")
        return self._type

    @measurement_type.setter
    @validate
    def measurement_type(self, value):
        self._visa.write(f"MEASUREMENT:MEAS{self._slot}:TYPE {value}")
        self._type = self._visa.query(f"MEASUREMENT:MEAS{self._slot}:TYPE?")

    @property
    def state(self):
        """value (str): ON or OFF"""
        self._state = self._visa.query(f"MEASUREMENT:MEAS{self._slot}:STATE?")
        return self._state

    @state.setter
    @validate
    def state(self, value):
        self._visa.write(f"MEASUREMENT:MEAS{self._slot}:STATE {value}")
        self._state = self._visa.query(f"MEASUREMENT:MEAS{self._slot}:STATE?")

    @property
    def value(self):
        """(float): measurement value"""
        return float(self._visa.query(f"MEASUREMENT:MEAS{self._slot}:VALUE?"))

    @property
    def min(self):
        """(float): minimum measurement value"""
        return float(self._visa.query(f"MEASUREMENT:MEAS{self._slot}:MINIMUM?"))

    @property
    def max(self):
        """(float): maximum measurement value"""
        return float(self._visa.query(f"MEASUREMENT:MEAS{self._slot}:MAXIMUM?"))

    @property
    def avg(self):
        """(float): average measurement value"""
        return float(self._visa.query(f"MEASUREMENT:MEAS{self._slot}:MEAN?"))

    @property
    def stddev(self):
        """(float): standard deviation of measurement"""
        return float(self._visa.query(f"MEASUREMENT:MEAS{self._slot}:STDDEV?"))

    @property
    def unit(self):
        """(str): unit of measurement"""
        return self._visa.query(f"MEASUREMENT:MEAS{self._slot}:UNITS?")

    def __repr__(self):
        return str(self.value)


class Probe(ProbeBase, kind="Probe"):
    """Oscilloscope probe

    Attributes:
        owner (Instrument): Instrument instance
        visa (pyvisa.resources.Resource): pyvisa resource
    """

    @property
    def model(self):
        """(str): probe model"""
        return self._visa.query(f"CH{self._ch}:PROBE:MODEL?").strip('"')

    @property
    def gain(self):
        """value (float): probe gain factor (output/input)"""
        return float(self._visa.query(f"CH{self._ch}:PROBE:GAIN?"))

    @gain.setter
    def gain(self, value):
        self._visa.write(f"CH{self._ch}:PROBE:GAIN {value}")

    @property
    def impedance(self):
        """value (float): probe impedance in ohms"""
        return float(self._visa.query(f"CH{self._ch}:PROBE:RESISTANCE?"))

    def __repr__(self):
        owner = self._owner.__repr__().strip("<>")
        return f"<{owner} {self._kind} {self.model}>"
