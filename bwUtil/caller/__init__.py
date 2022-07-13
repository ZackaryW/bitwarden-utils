from datetime import datetime as _datetime
from bwUtil.caller.client import BwBaseClient, BwCommunication
from bwUtil.caller.response import BwResponse
import os as _os
from functools import cached_property as _cached_property
import json as _json

class BwClient(BwBaseClient):
    def __init__(self, path: str) -> None:
        super().__init__(path)
        self.session = None
        self.lastSynced = None

    def _delCache(self, key):
        if key in self.__dict__:
            del self.__dict__[key]

    def simpleRun(self, *args) -> BwResponse:
        if self.session is not None:
            args = list(args) + ["--session", self.session]

        with self.createCommunication(*args) as proc:
            proc : BwCommunication
            return proc.commuicateObj()

    def runWithSession(self, *args):
        if self.session is None:
            raise Exception("session not present")
        args = list(args) + ["--session", self.session]
        with self.createCommunication(*args) as proc:
            proc : BwCommunication
            return proc.commuicateObj()


    @_cached_property
    def version(self):
        return self.simpleRun("--version").rawLines[0]

    @_cached_property
    def isLoggedIn(self):
        return self.simpleRun("login").login_is_logged_in

    def login(self, username, password, totp= None):
        args = ["login", username, password]
        if totp is not None:
            args.extend(["--method","0","--code", totp])

        with self.createCommunication(*args) as proc:
            proc : BwCommunication
            res = proc.commuicateObj()
            if "incorrect" in res.raw:
                return False
            if "logged in" not in res.rawLines[0]:
                return False
            self._delCache("isLoggedIn")
        self.session = res.session_extract
        return True

    def logout(self):
        with self.createCommunication("logout") as proc:
            self._delCache("isLoggedIn")
            return

    def unlock(self, password):
        res = self.simpleRun("unlock", password)

        self.session = res.session_extract

    def sync(self):
        res = self.runWithSession("sync")
        if "Syncing complete." in res.raw:
            self.lastSynced = _datetime.now()
            return True
        return False

    def get_attachment(self, item_id : str,item_name : str, attachment_name : str, output_path : str):
        if not _os.path.exists(_os.path.join(output_path, item_name)):
            _os.makedirs(_os.path.join(output_path, item_name), exist_ok=True)
        
        if _os.path.exists(_os.path.join(output_path, item_name, attachment_name)):
            return

        self.runWithSession(
            "get", 
            "attachment", attachment_name, 
            "--itemid", item_id,
            "--output", _os.path.join(output_path, item_name, attachment_name)
        )
        # change permission to everyone can read
        try:
            _os.chmod(_os.path.join(output_path, item_name), 0o777)
            _os.chmod(_os.path.join(output_path, item_name, attachment_name), 0o777)
        except:
            pass

    def export_attachments(self, output_path :str, rawData : list = None):
        if not rawData:
            if self.lastSynced is None and self.sync():
                pass
            
            rawData = self.runWithSession("list", "items", "--pretty")
            items = _json.loads(rawData.raw)
        else:
            items = rawData


        for i, item in enumerate(items):
            if "attachments" in item:
                for attachment in item["attachments"]:
                    self.get_attachment(
                        item_id=item["id"], 
                        item_name=item["name"],
                        attachment_name= attachment["fileName"], 
                        output_path = output_path
                    )
            yield i
            
    def export_items(self):
        rawData = self.runWithSession("list", "items", "--pretty")
        items = _json.loads(rawData.raw)    
        return items
        
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
