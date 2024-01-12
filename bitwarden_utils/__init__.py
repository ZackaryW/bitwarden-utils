from bitwarden_utils.core.python_client import BwPyClient
from bitwarden_utils.core.proc import BwProc, BwProcInfo
from bitwarden_utils.core.adapter import BwProcAdapter, BwProcCallback
from bitwarden_utils.core.history_recorder import HistoryRecorder

def download_all_attachments_in_one_go(
    targetFolder : str,
):
    import os
    os.makedirs(targetFolder, exist_ok = True)
    
    BwPyClient.sync()
    items = BwPyClient.listItems()
    if isinstance(items, str):
        raise Exception("An error occurred")
    for item in items:
        BwPyClient.downloadItemAttachment(
            item = item,
            folderPath = targetFolder   
        )
        
