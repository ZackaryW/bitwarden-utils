import os as _os
from bwUtil.download.request import downloadCli
import tempfile as _tempfile
import contextlib as _contextlib
import typing as _typing

def secureDownloadMethod(platform : _typing.Literal["windows", "linux", "macos"] = None):
    """
    this method will download the cli to a temp folder

    Args:
        platform (windows, linux, macos): Defaults to None and will automatically determine the platform

    Raises:
        ValueError: if the platform is not supported

    Returns:
        str: the path of the tempfolder that contains the cli

    #NOTE return is not the cli path but rather is the tempfolder path, make sure to either use
    os.listdir(path) or other iterative methods to get the cli path
    """

    if platform is None:
        os_type = _os.name
        match os_type:
            case "nt": platform = "windows"
            case "posix": platform = "linux"
            case "mac": platform = "macos"
            case _: raise ValueError("Unknown platform")

    tempdir = _tempfile.TemporaryDirectory()
    downloadCli(platform, tempdir.name, True)
    return tempdir
