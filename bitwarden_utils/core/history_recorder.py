
from dataclasses import dataclass
import datetime

from bitwarden_utils.core.adapter import BwProcAdapter, BwProcCallback


@dataclass
class HistoryRecorder(BwProcAdapter):
    max_records : int = 50
    
    def __init__(self):
        self.__records = []
        super().__init__()
        
    @BwProcCallback("post")
    def _record(self, *args):
        self.__records.append((datetime.datetime.now(), args))
        if len(self.__records) > self.max_records:
            self.__records.pop(0)
        return True
    
    @property
    def records(self):
        return self.__records
    

    