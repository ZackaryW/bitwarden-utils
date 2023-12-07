
import json
import os
from bitwarden_utils._internal.misc_models import Attachment, Item
from bitwarden_utils._internal.utils import is_size_within_range
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
        santized_name = sanitize_filename(f"[{item.id[0:6]}] {item.name}")

        for i, att in enumerate(item.attachments):
            print(f"Exporting {att['fileName']}, count {i+1}/{len(item.attachments)}")
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

        tarname = os.path.join(targetFolder, FolderName, att["fileName"])
        if is_size_within_range(tarname, int(att["size"])):
            print(f"File {att['fileName']} already exists, skipping")
            return

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
            
            print(f"Exporting {item.name}")
            self.__internal_export_attachment(item, folder)

            if limit > 0:
                limit -= 1
                if limit == 0:
                    break

    def sync(self, folder : str):
        for item in self.__internal_get_items():
            item : Item
            targetFolder = sanitize_filename(f"[{item.id[0:6]}] {item.name}")

            os.makedirs(os.path.join(folder, targetFolder), exist_ok=True)
            
            # list files
            files_exist_local = os.listdir(os.path.join(folder, targetFolder))
            files_exist_remote = [o["fileName"] for o in item.attachments] if item.attachments is not None else []
            
            # filter out files that exist on both sides
            files_pending_local = [f for f in files_exist_local if f not in files_exist_remote]
            files_pending_remote = [f for f in files_exist_remote if f not in files_exist_local]

            # download missing files
            for file in files_pending_remote:
                self.__internal_download_attachment(
                    file,
                    targetFolder,
                    item.id,
                    folder
                )
                print(f"Downloaded {file} for {item.name}")

            # upload missing files
            for file in files_pending_local:
                self.__proc.exec(
                    "create", 
                    "attachment", 
                    "--file", f"'{os.path.join(folder, targetFolder, file)}'",
                    "--itemid", item.id
                )
                print(f"Uploaded {file} for {item.name}")