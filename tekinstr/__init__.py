"""Tekinstr - the Pythonic way of communicating with Tektronix oscilloscopes"""
import pyvisa
from tekinstr.common import _get_idn
from tekinstr.mdo3000.mdo3000 import MDO3000
from tekinstr.tds3000.tds3000 import TDS3000
from tekinstr.mso4000b.mso4000b import MSO4000B
from tekinstr.version import __version__

MODEL_CLASS = {
    "MDO3012": MDO3000,
    "MDO3014": MDO3000,
    "MDO3022": MDO3000,
    "MDO3024": MDO3000,
    "MDO3032": MDO3000,
    "MDO3034": MDO3000,
    "MDO3052": MDO3000,
    "MDO3054": MDO3000,
    "MDO3102": MDO3000,
    "MDO3104": MDO3000,
    "TDS3064B": TDS3000,
    "MSO4104B": MSO4000B,
    "MSO4102B": MSO4000B,
    "MSO4014B": MSO4000B,
    "MSO4034B": MSO4000B,
    "MSO4054B": MSO4000B,
}


class CommChannel:
    """Connect to a Tektronix oscilloscope using VISA

    Attributes:
        address (str): instrument's TCPIP address or host name

    Returns:
        (CommChannel or Model subclass)
    """

    def __init__(self, address):
        self._address = address
        self._rm = pyvisa.ResourceManager()
        self._visa = self._rm.open_resource(f"TCPIP::{address}")
        self._visa.read_termination = "\n"

    def __enter__(self):
        # self._visa.lock_excl()
        self._visa.write("*CLS")
        idn = _get_idn(self._visa)
        if idn.manufacturer != "TEKTRONIX":
            raise ValueError(f"Device at {self._address} is not a Tektronix model")
        try:
            return MODEL_CLASS[idn.model](self._visa)
        except KeyError:
            raise NotImplementedError(f"{idn.model} not currently supported") from None

    def __exit__(self, exc_type, exc_value, exc_tb):
        # self._visa.unlock()
        self._visa.close()
        self._rm.close()

    def get_instrument(self):
        """Return the instrument object"""
        return self.__enter__()

    def close(self):
        """Close the CommChannel"""
        self.__exit__(None, None, None)


__all__ = ["CommChannel"]
