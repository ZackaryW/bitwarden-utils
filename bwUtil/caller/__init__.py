from dataclasses import dataclass
from bwUtil.caller.client import BwBaseClient, BwCommunication
from bwUtil.caller.response import BwResponse
import os as _os
from functools import cached_property as _cached_property

class BwClient(BwBaseClient):
    def __init__(self, path: str) -> None:
        super().__init__(path)
        self.session = None

    def _delCache(self, key):
        if key in self.__dict__:
            del self.__dict__[key]

    def simpleRun(self, *args):
        with self.createCommunication(*args) as proc:
            proc : BwCommunication
            return proc.commuicateObj()

    @_cached_property
    def version(self):
        return self.simpleRun("--version").raw[0]

    @_cached_property
    def isLoggedIn(self):
        return self.simpleRun("login").login_is_logged_in

    def login(self, username, password):
        with self.createCommunication("login", username, password) as proc:
            proc : BwCommunication
            raw = proc.commuicateObj().raw
            if "logged in" not in raw[0]:
                return False
            self._delCache("isLoggedIn")
        # '$ export BW_SESSION="{session}"'
        self.session = raw[3].split("=", 1)[1].strip('"')
        return True

    def logout(self):
        with self.createCommunication("logout") as proc:
            self._delCache("isLoggedIn")
            return

    @classmethod
    def find_nearby(cls):
        # check if BW_CLI_PATH is set
        if "BW_CLI_PATH" in _os.environ:
            return cls(_os.environ["BW_CLI_PATH"])

        cwd = _os.getcwd()
        for file in _os.listdir(cwd):
            if file.startswith("bw") and _os.path.isfile(file):
                return cls(_os.path.join(cwd, file))
        return None

    @classmethod
    def resolve(cls, path :str):
        if not path:
            return None

        if _os.path.exists(path) and _os.path.isfile(path):
            return cls(path)
        
        return cls.find_nearby()
