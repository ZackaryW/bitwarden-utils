
from dataclasses import dataclass
import os
from bitwarden_utils._internal.release_handler import GLOBAL_RELEASE_HANDLER
from bitwarden_utils.core.proc import BwProc
import tempfile

@dataclass(init=False)
class BWardenProc(BwProc):
    _version : str = None

    def __init__(self, version : str = None):
        self._version = version
        self.__tempdir = tempfile.TemporaryDirectory()

        if version is None:
            self.__release =  GLOBAL_RELEASE_HANDLER.get_latest_version()
        else:
            self.__release = GLOBAL_RELEASE_HANDLER.get_release_version(version)

        if self.__release is None:
            raise ValueError(f"Version {version} not found")
        
        self.__release.extractTo(self.__tempdir.name)

        file = os.listdir(self.__tempdir.name)[0]

        print("Extracted to", self.__tempdir.name + "/" + file)

        super().__init__(os.path.join(self.__tempdir.name, file))

    def __del__(self):
        self.__tempdir.cleanup()