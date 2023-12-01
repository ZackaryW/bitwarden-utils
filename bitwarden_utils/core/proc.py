from dataclasses import dataclass
import os
import subprocess

@dataclass(frozen=True)
class BwProc:
    path : str

    def __post_init__(self):
        if not os.path.exists(self.path) and not self.path == "bw":
            raise FileNotFoundError(f"{self.path} does not exist")
        
        self.__recorded_mdate = os.path.getmtime(self.path)

    def __prep_args(self, *args, session = None):
        cmd = [self.path]
        cmd += list(args)
        if session:
            cmd += ["--session", session]

        return cmd

    def exec(
        self, 
        *args, 
        session = None, 
        strip : bool =True
    ):
        if self.last_modified != self.__recorded_mdate:
            raise Exception("File has been tampered")

        args = self.__prep_args(*args, session=session)
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
