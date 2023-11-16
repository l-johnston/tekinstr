"""BUS"""
from tekinstr.instrument import InstrumentSubsystem
from tekinstr.common import validate


class Bus(InstrumentSubsystem, kind="Bus"):
    """Bus class

    Attributes:
        owner (Instrument)
    """

    def __init__(self, owner):
        super().__init__(owner)
        self._designation = "B1"

    @property
    def parameters(self):
        """Return the parameters for each serial and parallel bus"""
        return self._visa.query("BUS?")

    @property
    def state(self):
        """State of the bus {'ON', 'OFF'}"""
        res = self._visa.query(f"BUS:{self._designation}:STATE?")
        res_str = "ON" if res == "1" else "OFF"
        return res_str

    @state.setter
    @validate
    def state(self, value):
        self._visa.write(f"BUS:{self._designation}:STATE {value}")

    @property
    def bus_type(self):
        """Bus type {'I2C', 'SPI', 'PARALLEL'}"""
        return self._visa.query(f"BUS:{self._designation}:TYPE?")

    def threshold(self, channel, value=None):
        """Get or set the threshold for a bus channel

        Parameters
        ----------
            channel (str): {'CH1', 'CH2', 'CH3', 'CH4'}
            value (float): threshold voltage in volts, default is None
        """
        if value is not None:
            self._visa.write(f"BUS:THRESHOLD:{channel} {value}")
        return float(self._visa.query(f"BUS:THRESHOLD:{channel}?"))

    @property
    def label(self):
        """Label for the bus, limited to 30 characters"""
        res = self._visa.query(f"BUS:{self._designation}:LABEL?")
        res_str = res.replace('"', "")
        return res_str

    @label.setter
    @validate
    def label(self, value):
        value = f'"{value[:30]}"'
        self._visa.write(f"BUS:{self._designation}:LABEL {value}")


class I2CBus(Bus, kind="I2C Bus"):
    """I2C bus class

    Attributes:
        owner (Instrument)
    """

    def __init__(self, owner):
        super().__init__(owner)
        self._designation = "B1"

    @property
    def sclk_source(self):
        """Source for the SCLK signal {'CH1', 'CH2', 'CH3', 'CH4'}"""
        return self._visa.query(f"BUS:{self._designation}:I2C:SCLK:SOURCE?")

    @sclk_source.setter
    @validate
    def sclk_source(self, value):
        self._visa.write(f"BUS:{self._designation}:SCLK:SOURCE {value}")

    @property
    def sdata_source(self):
        """Source for the SDATA signal {'CH1', 'CH2', 'CH3', 'CH4'}"""
        return self._visa.query(f"BUS:{self._designation}:I2C:SDATA:SOURCE?")

    @sdata_source.setter
    @validate
    def sdata_source(self, value):
        self._visa.write(f"BUS:{self._designation}:I2C:SDATA:SOURCE {value}")

    @property
    def include_rw(self):
        """Include read/write bit in the address {'ON', 'OFF'}"""
        res = self._visa.query(f"BUS:{self._designation}:I2C:ADDRESS:RWINCLUDE?")
        res_str = "ON" if res == "1" else "OFF"
        return res_str

    @include_rw.setter
    @validate
    def include_rw(self, value):
        self._visa.write(f"BUS:{self._designation}:I2C:ADDRESS:RWINCLUDE {value}")

    @property
    def address_mode(self):
        """Address mode {'7-bit', '10-bit'}"""
        res = self._visa.query(f"TRIGGER:A:BUS:{self._designation}:I2C:ADDRESS:MODE?")
        return "7-bit" if res == "ADDR7" else "10-bit"

    @address_mode.setter
    @validate
    def address_mode(self, value):
        value = "ADDR7" if value == "7-bit" else "ADDR10"
        self._visa.write(f"TRIGGER:A:BUS:{self._designation}:I2C:ADDRESS:MODE {value}")

    @property
    def address_type(self):
        """Address type {'GeneralCall', 'StartByte', 'HSMode', 'EEPROM', 'User'}"""
        res = self._visa.query(f"TRIGGER:A:BUS:{self._designation}:I2C:ADDRESS:TYPE?")
        return res

    @property
    def address_value(self):
        """Address to trigger on"""
        return self._visa.query(f"TRIGGER:A:BUS:{self._designation}:I2C:ADDRESS:VALUE?")

    @address_value.setter
    @validate
    def address_value(self, value):
        self._visa.write(f"TRIGGER:A:BUS:{self._designation}:I2C:ADDRESS:VALUE {value}")

    @property
    def condition(self):
        """Condition to trigger on {'Start', 'Stop', 'RepeatStart', 'Address', 'Data'}"""
        return self._visa.query(f"TRIGGER:A:BUS:{self._designation}:I2C:CONDITION?")

    @condition.setter
    @validate
    def condition(self, value):
        self._visa.write(f"TRIGGER:A:BUS:{self._designation}:I2C:CONDITION {value}")

    @property
    def data_direction(self):
        """Data direction to trigger on {'Read', 'Write', 'NoCare'}"""
        return self._visa.query(
            f"TRIGGER:A:BUS:{self._designation}:I2C:DATA:DIRECTION?"
        )

    @data_direction.setter
    @validate
    def data_direction(self, value):
        self._visa.write(
            f"TRIGGER:A:BUS:{self._designation}:I2C:DATA:DIRECTION {value}"
        )

    @property
    def data_size(self):
        """Data size to trigger on, integer bytes"""
        res = self._visa.query(f"TRIGGER:A:BUS:{self._designation}:I2C:DATA:SIZE?")
        return int(res)

    @data_size.setter
    @validate
    def data_size(self, value):
        self._visa.write(f"TRIGGER:A:BUS:{self._designation}:I2C:DATA:SIZE {value}")

    @property
    def data_value(self):
        """Data to trigger on, binary string {0, 1, X}"""
        return self._visa.query(f"TRIGGER:A:BUS:{self._designation}:I2C:DATA:VALUE?")

    @data_value.setter
    @validate
    def data_value(self, value):
        value = f'"{value}"'
        self._visa.write(f"TRIGGER:A:BUS:{self._designation}:I2C:DATA:VALUE {value}")
