from datetime import datetime as _datetime
from bwUtil.caller.client import BwBaseClient, BwCommunication
from bwUtil.caller.response import BwResponse
import os as _os
from functools import cached_property as _cached_property
import json as _json

class BwClient(BwBaseClient):
    """
    bw cli wrapper
    """

    def __init__(self, path: str) -> None:
        super().__init__(path)
        self.session = None
        self.lastSynced = None

    def _delCache(self, key):
        """
        resets cache_property
        """
        if key in self.__dict__:
            del self.__dict__[key]

    def simpleRun(self, *args) -> BwResponse:
        """
        this method wraps around creating, running and closing a communication
        """

        if self.session is not None:
            args = list(args) + ["--session", self.session]

        with self.createCommunication(*args) as proc:
            proc : BwCommunication
            return proc.commuicateObj()

    def runWithSession(self, *args):
        """
        this method calls simpleRun with session as suffix

        Raises:
            Exception: if session is not set
        """

        if self.session is None:
            raise Exception("session not present")
        args = list(args) + ["--session", self.session]
        with self.createCommunication(*args) as proc:
            proc : BwCommunication
            return proc.commuicateObj()


    @_cached_property
    def version(self):
        """
        returns the version of the bw cli
        """

        return self.simpleRun("--version").rawLines[0]

    @_cached_property
    def isLoggedIn(self):
        """
        returns true if logged in
        """

        return self.simpleRun("login").login_is_logged_in

    def login(self, username, password, totp= None):
        """
        logs in to bitwarden
        """

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
        """
        logs out of bitwarden
        """
        with self.createCommunication("logout") as proc:
            self._delCache("isLoggedIn")
            return

    def unlock(self, password):
        """
        unlocks bitwarden
        """

        res = self.simpleRun("unlock", password)

        self.session = res.session_extract

    def sync(self):
        """
        syncs bitwarden
        """

        res = self.runWithSession("sync")
        if "Syncing complete." in res.raw:
            self.lastSynced = _datetime.now()
            return True
        return False

    def listItems(self):
        """
        lists all items in bitwarden
        """

        res = self.simpleRun("list", "items", "--pretty")
        items = _json.loads(res.raw)
        return items

    def get_attachment(self, item_id : str,item_name : str, attachment_name : str, output_path : str):
        """
        downloads an attachment from bitwarden

        Args:
            item_id (str)
            item_name (str)
            attachment_name (str)
            output_path (str)
        """

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
        """
        exports all attachments from bitwarden to a given path

        Args:
            output_path (str)
            rawData (list, optional): already exported data from other methods. used to cut down on calls to bitwarden. Defaults to None.

        Yields:
            i : the current count of progress

        UseCase:
            it can be used as a generator

        ```py
        for i in bw.export_attachments(output_path):
            # output progress
        ```
        """

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
            yield i+1
            
    def export_items(self):
        rawData = self.runWithSession("list", "items", "--pretty")
        items = _json.loads(rawData.raw)    
        return items
        
    @classmethod
    def find_nearby(cls, lv_accepted : int = 1)-> 'BwClient':
        """
        attempts to find a bitwarden cli in cwd and environment variables

        returns None if not found
        """
        def dig_dir(path, lv_accepted = 1):
            if lv_accepted <= 0:
                return None

            for root, dirs, files in _os.walk(path):
                for file in files:
                    filePath = _os.path.join(root, file)
                    if _os.path.getsize(filePath) <= 10 * 1024 * 1024:
                        continue
                    if not file.startswith("bw"):
                        continue
                    if not _os.path.isfile(filePath):
                        continue
                    if filePath.endswith(".py"):
                        continue
                    
                    return _os.path.join(root, file)
                for dir in dirs:
                    if dir.startswith("."):
                        continue

                    res = dig_dir(_os.path.join(root, dir), lv_accepted - 1)
                    if res is not None:
                        return res

        # check if BW_CLI_PATH is set
        if "BW_CLI_PATH" in _os.environ:
            return cls(_os.environ["BW_CLI_PATH"])

        cwd = _os.getcwd()
        try:
            res = dig_dir(cwd, lv_accepted)
        except:
            res = None
        if res is not None:
            return cls(res)
        return None

    @classmethod
    def resolve(cls, path :str):

        if not path:
            return None

        if _os.path.exists(path) and _os.path.isfile(path):
            return cls(path)
        
        return cls.find_nearby()
