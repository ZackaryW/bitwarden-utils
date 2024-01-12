
import typing
import json
import os

from bitwarden_utils.core.session_retain import (
    InMemorySR,
    SessionRetainInterface
)
from bitwarden_utils.core.models.status import Status
from bitwarden_utils.core.utils import classproperty, session_extract
import subprocess

class BwProc:
    path : str = "bw"
    sessionR : SessionRetainInterface = lambda : None # noqa
    sessionRType : typing.Type[SessionRetainInterface] = InMemorySR
    
    clientValidation : typing.Callable = None
    
    @classproperty
    def info(cls):
        return BwProcInfo
    
    @classmethod
    def setSessionType(
        cls, type : typing.Literal["memory"]
    ):
        match type:
            case "memory":
                cls.sessionRType = InMemorySR
            case _:
                raise NotImplementedError
    
    @classmethod
    def login(
        cls,
        username : str,
        password : str,
        totp : str = None,
        path : str = "bw",
    ):
        args = ["login", username, password]
        if totp:
            args += ["--method", "0","--code", totp]

        cls.path = path
        if BwProcInfo.status["status"] != "unauthenticated":
            raise Exception("Already logged in, please use unlock")

        res = cls.exec(*args)
        cls.sessionR = cls.sessionRType(session_extract(res))
    
    @classmethod
    def __prep_args(cls, *args):
        cmd = [cls.path]
        cmd += list([str(x) for x in args])
        session = cls.sessionR()
        if session:
            cmd += ["--session", session]
        return cmd

    @classmethod
    def exec(
        cls, 
        *args, 
        strip : bool =True
    ):
        if cls.clientValidation is not None and not cls.clientValidation(BwProcInfo):
            raise Exception("Client validation failed")
            
        args = cls.__prep_args(*args)
        ret = subprocess.run(args, stdout=subprocess.PIPE, check=True)
        # decode
        ret_output = ret.stdout.decode()

        if strip:
            ret_output = ret_output.strip()

        return ret_output
    
    @classmethod
    def unlock(
        cls,
        password : str,
        path : str = "bw",
    ):
        args = ["unlock", password]
        cls.path = path

        res = cls.exec(*args)
        cls.sessionR = cls.sessionRType(session_extract(res))

    
class BwProcInfo:
    @classproperty
    def last_modified(cls):
        if cls.only_bw:
            return None
        
        return os.path.getmtime(BwProc.path)
    
    @classproperty
    def last_accessed(cls):
        if cls.only_bw:
            return None
        
        return os.path.getatime(BwProc.path)
    
    @classproperty
    def only_bw(cls):
        return BwProc.path == "bw"

    @classproperty
    def version(cls):
        return BwProc.exec("--version")
    
    @classproperty
    def status(cls) -> Status:
        return json.loads(BwProc.exec("status"))

    @classproperty
    def isLocked(cls):
        return cls.status["status"] == "locked"
    
info_methods = {
    x: BwProcInfo.__dict__[x] for x in dir(BwProcInfo) if not x.startswith("_")
}

proc_methods = {
    x : BwProc.__dict__[x] for x in dir(BwProc) if not x.startswith("_")
}