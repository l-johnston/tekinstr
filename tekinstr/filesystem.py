"""Base file system definition"""
from tekinstr.instrument import Instrument
from tekinstr.common import validate


class FileSystemBase(Instrument, kind="FileSystemBase"):
    """File system

    Attributes:
        instr (Model)
    """

    @property
    def listing(self):
        """Return the current directory listing"""
        result = self._visa.query("FILESYSTEM?")
        raw_listing, _ = result.split(";")
        listing = raw_listing.replace('"', "").split(",")
        return listing

    @property
    def cwd(self):
        """Current working directory

        Parameters
        ----------
        value : str
            change working directory to 'value' e.g. 'E:/data'
        """
        result = self._visa.query("FILESYSTEM:CWD?")
        return result.replace('"', "")

    @cwd.setter
    @validate
    def cwd(self, value):
        self._visa.write(f"FILESYSTEM:CWD '{value}'")

    def mkdir(self, directory):
        """Make 'directory' at current working directory

        Parameters
        ----------
        directory : str
        """
        self._visa.write(f"FILESYSTEM:MKDIR '{directory}'")
