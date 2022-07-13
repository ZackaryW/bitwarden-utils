import subprocess as _subprocess
import sys as _sys
import os as _os
import typing as _typing
import contextlib as _contextlib
from asyncio.subprocess import Process as _Process

from bwUtil.caller.response import BwResponse

class BwCommunication:
    def __init__(self, process : _Process) -> None:
        self.proc = process

    def communicate(self, *args, **kwargs) -> str:
        # to bytes
        for i, arg in enumerate(args):
            if isinstance(arg, str):
                args[i] = arg.encode("utf-8")        

        return self.proc.communicate(*args)

    def commuicateObj(self,  *args, **kwargs) -> BwResponse:
        output =  self.communicate(*args, **kwargs)[0].decode("utf-8")
        return BwResponse(output)
        
class BwBaseClient:
    def __init__(self, path : str) -> None:
        if not _os.path.isfile(path) and not _os.path.exists(path):
            raise FileNotFoundError(f"Could not find file at {path}")
        
        # change file in path readonly and no del
        self._current_path_permision = _os.stat(path).st_mode
        import stat
        _os.chmod(path, 0o555)
        
        self.path = path

    def __del__(self):
        _os.chmod(self.path, self._current_path_permision)

    @_contextlib.contextmanager
    def createCommunication(self, *args) -> BwCommunication:
        self.comm = None

        try:
            args = [self.path] + list(args)
            proc : _Process = _subprocess.Popen(args, stdin=_subprocess.PIPE, stdout=_subprocess.PIPE, stderr=_subprocess.STDOUT)
            self.comm = BwCommunication(proc)
            yield self.comm
        finally:
            if not self.comm:
                return

            self.comm.proc.stdin.close()
            self.comm.proc.stdout.close()
            self.comm.proc.wait()
            del self.comm
            self.comm = None