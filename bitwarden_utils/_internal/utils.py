
import typing
import hashlib

def checksum_verify(filecontent : bytes, checksum : typing.Union[str, bytes]):
    checksum = checksum.strip()
    if isinstance(checksum, bytes):
        checksum = checksum.decode("utf-8")

    file_sha256 = hashlib.sha256(filecontent).hexdigest().upper()

    if file_sha256 == checksum.upper():
        return True
    else:
        return False
    

