from bitwarden_utils.core.proc import BwProc
import json

from bitwarden_utils.core.models.item import Attachment, BwItem
import os

class BwPyClient:
    @staticmethod
    def sync():
        return BwProc.exec("sync")
    
    @staticmethod
    def listItems():
        raw =  BwProc.exec("list", "items","--pretty")
        try:
            rawjson = json.loads(raw)
            rawitems = [BwItem(**item) for item in rawjson]
        except: # noqa
            return raw
        return rawitems
    
    @staticmethod
    def downloadAttachment(
        attachment : Attachment,
        itemId : str,
        folderPath :str,
        performFolderCheck : bool = False
    ):
        BwProc.exec(
            "get",
            "attachment", attachment["fileName"],
            "--itemid", itemId,
            "--output", os.path.join(folderPath, attachment["fileName"]),
        )
    
    @staticmethod
    def formatString(
        item : BwItem = None,
        attachment : Attachment = None,
        format : str = "[{itemIdShorthand}] {itemName}"
    ):
        return format.format(
            itemIdShorthand = item["id"][:6] if item else "",
            itemName = item["name"] if item else "",
            fileName = attachment["fileName"] if attachment else "",
            fileSize = attachment["sizeName"] if attachment else "",
        )
    
    @staticmethod
    def downloadItemAttachment(
        item : BwItem,
        folderPath :str,
        makeNewFolder : bool = True,
        newFolderFormatting : str = "[{itemIdShorthand}] {itemName}"
    ):
        if makeNewFolder:
            folderPath = os.path.join(folderPath, BwPyClient.formatString(item = item, format = newFolderFormatting))
        os.makedirs(folderPath, exist_ok = True)
        for attachment in item.attachments:
            BwPyClient.downloadAttachment(
                attachment = attachment,
                itemId = item.id,
                folderPath = folderPath
            )
        
    