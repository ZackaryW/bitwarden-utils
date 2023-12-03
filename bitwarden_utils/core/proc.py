from dataclasses import dataclass
import json
import os
import subprocess
from typing import Any

from bitwarden_utils._internal.misc_models import Status

@dataclass
class BwProc:
    path : str = "bw"
    session : str = None

    def __setattr__(self, __name: str, __value: Any) -> None:
        if __name == "path" and "path" in self.__dict__:
            raise Exception("Cannot change path")
        super().__setattr__(__name, __value)

    def __post_init__(self):
        if not os.path.exists(self.path) and not self.path == "bw":
            raise FileNotFoundError(f"{self.path} does not exist")
        
        if not self.only_bw:
            self.__recorded_mdate = os.path.getmtime(self.path)

    def __prep_args(self, *args):
        cmd = [self.path]
        cmd += list([str(x) for x in args])
        if self.session:
            cmd += ["--session", self.session]

        return cmd

    def exec(
        self, 
        *args, 
        strip : bool =True
    ):
        if not self.only_bw and self.last_modified != self.__recorded_mdate:
            raise Exception("File has been tampered")

        args = self.__prep_args(*args)
        ret = subprocess.run(args, stdout=subprocess.PIPE, check=True)
        # decode
        ret_output = ret.stdout.decode()

        if strip:
            ret_output = ret_output.strip()

        return ret_output

    @property
    def last_modified(self):
        if self.only_bw:
            return None
        
        return os.path.getmtime(self.path)
    
    @property
    def last_accessed(self):
        if self.only_bw:
            return None
        
        return os.path.getatime(self.path)
    
    @property
    def only_bw(self):
        return self.path == "bw"

    @property
    def version(self):
        return self.exec("--version")
    
    @property
    def status(self)-> Status:
        return json.loads(self.exec("status"))

    @property
    def isLocked(self):
        return self.status["status"] == "locked"

    @staticmethod
    def __session_extract(raw):
        """
        it will extract the session from the raw response

        Returns:
            str: session if present else None
        """

        if "$ export BW_SESSION" not in raw:
            return None
        
        rawlines = raw.split("\n")
        try:
            for line in rawlines:
                if "$ export BW_SESSION" in line:
                    eline = line.split("=", 1)[1].strip('"').split('"')[0]
                    return eline
        except Exception:
            return None

    @classmethod
    def login(
        cls,
        path : str,
        username : str,
        password : str,
        totp : str = None
    ):
        args = ["login", username, password]
        if totp:
            args += ["--method", "0","--code", totp]

        proc = cls(path)
        if proc.status["status"] != "unauthenticated":
            raise Exception("Already logged in, please use unlock")

        res = proc.exec(*args)
        proc.session = cls.__session_extract(res)
        return proc

    @classmethod
    def unlock(
        cls,
        password : str,
        path : str = "bw",
    ):
        args = ["unlock", password]
        proc = cls(path)

        res = proc.exec(*args)
        proc.session = cls.__session_extract(res)
        return proc
    