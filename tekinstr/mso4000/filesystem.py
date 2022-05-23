"""File system"""
import pathlib
from tekinstr.filesystem import FileSystemBase


class FileSystem(FileSystemBase, kind="FileSystem"):
    """File system

    Attributes:
        instr (Model)
    """

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
