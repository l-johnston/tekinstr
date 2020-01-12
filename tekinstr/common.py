"""Common definitions"""
from collections import namedtuple
import functools

IDN = namedtuple("IDN", ["manufacturer", "model", "serial_number", "firmware_version"])


def _get_idn(visa):
    idn = visa.query("*IDN?").strip(":\n").split(",")
    manufacturer = idn[0]
    model = idn[1].replace(" ", "")
    serial_number = idn[2]
    versions = dict([field.split(":") for field in idn[3].split(" ")])
    firmware_version = versions["FV"]
    return IDN(manufacturer, model, serial_number, firmware_version)


class CommandError(Exception):
    """Raised when CME bit of SESR is set"""


def validate(func):
    """Read the Command Error bit (CME) of the Standard Event Status Register (SESR)"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # pylint: disable=protected-access
        cme = 32
        self = args[0]
        self._visa.write("*CLS")
        original_deser = int(self._visa.query("DESE?"))
        self._visa.write(f"DESE {cme}")
        result = func(*args, **kwargs)
        if bool(int(self._visa.query("*ESR?")) & cme):
            msg = self._visa.query("EVMSG?").strip().split(",")[1].strip('"')
            self._visa.write(f"DESE {original_deser}")
            raise CommandError(msg)
        self._visa.write(f"DESE {original_deser}")
        return result

    return wrapper


class TekBase:
    """tekinstr base class

    Attributes:
        visa (pyvisa.resources.Resource): pyvisa resource
    """

    def __init__(self, visa):
        self._visa = visa

    def __setattr__(self, name, value):
        if hasattr(self, name) and isinstance(getattr(self, name), TekBase):
            raise AttributeError(f"can't set '{name}'")
        if hasattr(self.__class__, name):
            prop = getattr(self.__class__, name)
            try:
                prop.fset(self, value)
            except TypeError:
                raise AttributeError(f"can't set '{name}'") from None
        else:
            self.__dict__[name] = value

    def __repr__(self):
        raise NotImplementedError

    def __dir__(self):
        inst_attr = list(filter(lambda k: not k.startswith("_"), self.__dict__.keys()))
        cls_attr = list(filter(lambda k: not k.startswith("_"), dir(self.__class__)))
        return inst_attr + cls_attr
