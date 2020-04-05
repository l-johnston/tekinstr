"""Measurement subsystem"""
from unyt import unyt_quantity
from tekinstr.common import validate
from tekinstr.instrument import InstrumentSubsystem


class Measurement(InstrumentSubsystem, kind="Measurement"):
    """Automated measurement system of the oscilloscope

    Attributes:
        owner (Instrument)
        n_slots (int): numbers of measurement slots
    """

    def __init__(self, owner, n_slots):
        super().__init__(owner)
        self._n_slots = n_slots
        self._has_stats = self._has_stats_hw()
        self._slots = [MeasurementSlot(self, i) for i in range(1, n_slots + 1)]
        self._initialize()

    def _has_stats_hw(self):
        original_deser = int(self._visa.query("DESE?"))
        self._visa.write("DESE 16")  # check only for EXE bit
        self._visa.write("*CLS")
        self._visa.write("MEASUREMENT:MEAS1:MEAN?")
        self._visa.query("*ESR?")
        msgs = self._visa.query("EVENT?").split("\n")
        event_code = int(msgs[-1])
        self._visa.write(f"DESE {original_deser}")
        return event_code == 0

    def _initialize(self):
        for i in range(1, self._n_slots + 1):
            q_str = f"MEASUREMENT:MEAS{i}:"
            state = self._visa.query(q_str + "STATE?")
            if state in ["1", "ON"]:
                source = self._visa.query(q_str + "SOURCE?").lower()
                measurement_type = self._visa.query(q_str + "TYPE?").lower()
                measurement = self._slots[i - 1]
                setattr(self, source + "_" + measurement_type, measurement)

    def add(self, source, measurement_type):
        """Add a measurement

        Args:
            source (str): source channel; CHx
            measurement_type (str): type of measurement; amplitude, frequency, etc.
        """
        for slot in self._slots:
            if slot.state in ["0", "OFF"]:
                measurement = slot
                break
        else:
            raise ValueError("No measurement slots available. Remove a measurement")
        measurement.source = source
        measurement.measurement_type = measurement_type
        measurement.state = "ON"
        setattr(self, source + "_" + measurement_type, measurement)

    def remove(self, name):
        """Remove a measurement

        Args:
            name (str): measurement name
        """
        measurement = getattr(self, name, None)
        if measurement is None:
            raise ValueError(f"Unknown measurement {name}")
        measurement.state = "OFF"
        delattr(self, name)


class MeasurementSlot(InstrumentSubsystem, kind="MeasurementSlot"):
    """A measurement slot

    Attributes:
        owner (Measurement)
        slot (int): measurement slot
    """

    def __init__(self, owner, slot):
        super().__init__(owner)
        self._slot = slot
        self._has_stats = owner._has_stats

    @property
    def source(self):
        """value (str): source channel; CHx"""
        q_str = f"MEASUREMENT:MEAS{self._slot}:SOURCE?"
        return self._visa.query(q_str)

    @source.setter
    @validate
    def source(self, value):
        cmd_str = f"MEASUREMENT:MEAS{self._slot}:SOURCE {value}"
        self._visa.write(cmd_str)

    @property
    def measurement_type(self):
        """value (str): measurement type; amplitude, frequency, etc."""
        q_str = f"MEASUREMENT:MEAS{self._slot}:TYPE?"
        return self._visa.query(q_str)

    @measurement_type.setter
    @validate
    def measurement_type(self, value):
        cmd_str = f"MEASUREMENT:MEAS{self._slot}:TYPE {value}"
        self._visa.write(cmd_str)

    @property
    def state(self):
        """value (str): {ON, OFF}"""
        q_str = f"MEASUREMENT:MEAS{self._slot}:STATE?"
        return self._visa.query(q_str)

    @state.setter
    @validate
    def state(self, value):
        cmd_str = f"MEASUREMENT:MEAS{self._slot}:STATE {value}"
        self._visa.write(cmd_str)

    @property
    def value(self):
        """(float): measurement value"""
        q_str = f"MEASUREMENT:MEAS{self._slot}:VALUE?"
        return float(self._visa.query(q_str))

    @property
    def min(self):
        """(float): minimum measurement value"""
        q_str = f"MEASUREMENT:MEAS{self._slot}:MINIMUM?"
        return float(self._visa.query(q_str))

    @property
    def max(self):
        """(float): maximum measurement value"""
        q_str = f"MEASUREMENT:MEAS{self._slot}:MAXIMUM?"
        return float(self._visa.query(q_str))

    @property
    def avg(self):
        """(float): average measurement value"""
        q_str = f"MEASUREMENT:MEAS{self._slot}:MEAN?"
        return float(self._visa.query(q_str))

    @property
    def stddev(self):
        """(float): standard deviation of measurement"""
        q_str = f"MEASUREMENT:MEAS{self._slot}:STDDEV?"
        return float(self._visa.query(q_str))

    @property
    def unit(self):
        """(str): unit of measurement"""
        q_str = f"MEASUREMENT:MEAS{self._slot}:UNITS?"
        return self._visa.query(q_str).strip('"')

    def __repr__(self):
        return str(unyt_quantity(self.value, self.unit))

    def __dir__(self):
        attrs = super().__dir__()
        for attr in ["source", "measurement_type", "state", "unit"]:
            attrs.remove(attr)
        if not self._has_stats:
            for attr in ["min", "max", "avg", "stddev"]:
                attrs.remove(attr)
        return attrs
