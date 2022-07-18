import subprocess as _subprocess
import sys as _sys
import os as _os
import typing as _typing
import contextlib as _contextlib
from asyncio.subprocess import Process as _Process

from bwUtil.caller.response import BwResponse

class BwCommunication:
    """
    a wrapper of subprocess call that returns a BwResponse
    """

    def __init__(self, process : _Process) -> None:
        self.proc = process

    def communicate(self, *args, **kwargs) -> str:
        """
        this is equivalent to subprocess.communicate() with all args being utf-8 encoded

        NOTE: kwargs are currently not in any use

        Returns:
            expected returns of subprocess.communicate()
        """
        # to bytes
        args = list(args)
        for i, arg in enumerate(args):
            if isinstance(arg, str):
                args[i] = arg.encode("utf-8")        

        return self.proc.communicate(*args)

    def commuicateObj(self,  *args, **kwargs) -> BwResponse:
        """
        the returns of subprocess communicate after calling communicate() will be wrapped in a BwResponse object

        NOTE: kwargs are currently not in any use
        """

        output =  self.communicate(*args, **kwargs)[0].decode("utf-8")
        return BwResponse(output)
        
class BwBaseClient:
    def __init__(self, path : str) -> None:
        """
        initialize the client with the path of the cli

        Args:
            path (str): cli path

        Raises:
            FileNotFoundError: if the path is not found
        """

        if not _os.path.isfile(path) and not _os.path.exists(path):
            raise FileNotFoundError(f"Could not find file at {path}")
        
        # change file in path readonly and no del
        self._current_path_permision = _os.stat(path).st_mode
        import stat
        _os.chmod(path, 0o555)
        
        self.path = path

    def __del__(self):
        # restore file permissions
        _os.chmod(self.path, self._current_path_permision)

    @_contextlib.contextmanager
    def createCommunication(self, *args) -> BwCommunication:
        """
        Returns:
            BwCommunication: a wrapper of subprocess.Process

        Usage Example:
        ```py
            with client.createCommunication("--version") as proc:
                proc : BwCommunication
                res = proc.commuicateObj()

                # res.raw is the output of the cli
        ```

        """
        if not hasattr(self, "comm"):
            self.comm = None

        if self.comm is not None:
            raise Exception("comm is already set")
        

        try:
            args = [self.path] + list(args)
            args = [str(arg).encode("utf-8") for arg in args]

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