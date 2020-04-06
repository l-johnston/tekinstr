"""Model base class"""
from datetime import datetime
from tekinstr.common import TekBase, _get_idn


class Model(TekBase):
    """Base class for a given model

    Attributes:
        visa (pyvisa.resources.Resource): pyvisa resource
    """

    def __init__(self, visa):
        super().__init__(visa)
        self._visa.write("HEADER OFF")
        self._visa.write("DESE 255")
        self._visa.write("VERBOSE ON")
        self._idn = _get_idn(visa)

    @property
    def model(self):
        """(str): the model number"""
        return self._idn.model

    @property
    def serial_number(self):
        """(str): the serial number"""
        return self._idn.serial_number

    @property
    def firmware_version(self):
        """(str): the firmware version"""
        return self._idn.firmware_version

    def lock_frontpanel(self, message=None):
        """Lock the front panel controls

        Args:
            message (str): message to display, such as "In use by ..."
        """
        self._visa.write("LOCK ALL")
        if message is not None:
            message = message[:1000]
            self._visa.write(f"MESSAGE:SHOW '{message[:1000]}'")
            self._visa.write("MESSAGE:BOX 0, 0")
            self._visa.write("MESSAGE:STATE ON")

    def unlock_frontpanel(self):
        """Unlock the front panel controls and clear message box if displayed"""
        self._visa.write("UNLOCK ALL")
        self._visa.write("MESSAGE:CLEAR")
        self._visa.write("MESSAGE:STATE OFF")

    def reset(self):
        """Reset the oscilloscope to the factory default settings"""
        self._visa.write("*RST")

    def set_clock(self):
        """Set the date and time to the local machine's time"""
        self._visa.write(f"DATE '{datetime.now().strftime('%Y-%m-%d')}'")
        self._visa.write(f"TIME '{datetime.now().strftime('%H:%M:%S')}'")

    @property
    def time(self):
        t_str = self._visa.query("TIME?").replace('"', "")
        d_str = self._visa.query("DATE?").replace('"', "")
        return f"{d_str} {t_str}"

    def __repr__(self):
        return f"<Tektronix {self.model} at {self._visa.resource_name}>"
