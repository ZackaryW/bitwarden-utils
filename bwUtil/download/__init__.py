import os as _os
from bwUtil.download.request import downloadCli
import tempfile as _tempfile
import contextlib as _contextlib
import typing as _typing

def secureDownloadMethod(platform : _typing.Literal["windows", "linux", "macos"] = None):
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
