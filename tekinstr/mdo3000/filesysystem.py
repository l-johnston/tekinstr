"""File system"""
import pathlib
from tekinstr.instrument import Instrument
from tekinstr.common import validate


class FileSystem(Instrument, kind="FileSystem"):
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

    def mount(self, path, drive, username="", password=""):
        """Mount a network drive at 'path' to instrument file system 'drive'

        Only supports Microsoft Windows NFS or CIFS networks.
        Caution: username and password are in-the-clear

        Parameters
        ----------
        path : str
            network path e.g. '<server>/this/that/mydir'
        drive : str
            instrument file system, network drives start at 'G:'
        username : str
        password : str
        """
        parts = pathlib.PurePath(path).parts
        server, path = (parts[0], "/".join(parts[1:]))
        cmd = ";".join([drive, server, path, username, password])
        self._visa.write(f"FILESYSTEM:MOUNT:DRIVE '{cmd}'")

    def unmount(self, drive):
        """Unmount network 'drive'

        Parameters
        ----------
        drive : str
            drive to unmount e.g. 'G:'
        """
        self._visa.write(f"FILESYSTEM:UNMOUNT:DRIVE '{drive}'")

    def mkdir(self, directory):
        """Make 'directory' at current working directory

        Parameters
        ----------
        directory : str
        """
        self._visa.write(f"FILESYSTEM:MKDIR '{directory}'")
