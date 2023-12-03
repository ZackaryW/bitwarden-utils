
import json
import os
from bitwarden_utils._internal.misc_models import Attachment, Item
from bitwarden_utils.core.proc import BwProc
from pathvalidate import sanitize_filename

class AttachmentManager:
    def __init__(self, proc : BwProc):
        if not isinstance(proc, BwProc):
            raise TypeError("proc must be of type BwProc")
        
        if not proc.status["status"] == "unlocked":
            raise Exception("bw is not unlocked")
        
        self.__proc = proc

    def __internal_export_attachment(
        self,
        item : Item,
        targetFolder : str
    ):
        santized_name = sanitize_filename(item.name)

        for att in item.attachments:
            self.__internal_download_attachment(
                att,
                santized_name,
                item.id,
                targetFolder
            )

    def __internal_download_attachment(
        self,
        att : Attachment,
        FolderName : str,
        itemId : str,
        targetFolder : str
    ):
        if not os.path.exists(os.path.join(targetFolder, FolderName)):
            os.makedirs(os.path.join(targetFolder, FolderName))

        self.__proc.exec(
            "get",
            "attachment", att["fileName"],
            "--itemid", itemId,
            "--output", os.path.join(targetFolder, FolderName, att["fileName"]),
        )

    def __internal_get_items(self):
        raw = self.__proc.exec("list", "items","--pretty")
        rawjson = json.loads(raw)
        rawitems = [Item(**item) for item in rawjson]

        return rawitems

    def export(self, folder : str, limit : int = -1):
        if not os.path.exists(folder):
            os.makedirs(folder)

        for item in self.__internal_get_items():
            if item.attachments is None:
                continue

            self.__internal_export_attachment(item, folder)

            if limit > 0:
                limit -= 1
                if limit == 0:
                    break