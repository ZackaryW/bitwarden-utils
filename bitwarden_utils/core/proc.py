
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
    def __init__(self) -> None:
        raise Exception("Not meant to be instantiated")
    
    path : str = "bw"
    sessionR : SessionRetainInterface = None 
    sessionRType : typing.Type[SessionRetainInterface] = InMemorySR
    
    preExecCallbacks : typing.List[typing.Callable] = []
    postExecCallbacks : typing.List[typing.Callable] = []
        
    @classproperty
    def info(cls) -> 'BwProcInfo':
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
    def __get_session(cls):
        if cls.sessionR is None:
            return None
    
        return cls.sessionR()
    
    @classmethod
    def __prep_args(cls, *args):
        cmd = [cls.path]
        cmd += list([str(x) for x in args])
        session = cls.__get_session()
        if session:
            cmd += ["--session", session]
        return cmd

    @classmethod
    def exec(
        cls, 
        *args, 
        strip : bool =True
    ):
        for method in BwProc.preExecCallbacks:
            method()
            
        args = cls.__prep_args(*args)
        ret = subprocess.run(args, stdout=subprocess.PIPE, check=True)
        # decode
        ret_output = ret.stdout.decode()

        if strip:
            ret_output = ret_output.strip()

        for method in BwProc.postExecCallbacks:
            method(ret_output)
        
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
    def __init__(self) -> None:
        raise Exception("Not meant to be instantiated")
    
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
    
    @classproperty
    def notLoggedIn(cls):
        return cls.status["status"] == "unauthenticated"
    
info_methods = {
    x: BwProcInfo.__dict__[x] for x in dir(BwProcInfo) if not x.startswith("_")
}

proc_methods = {
    x : BwProc.__dict__[x] for x in dir(BwProc) if not x.startswith("_")
}