
import typing
import hashlib
import os

def checksum_verify(filecontent : bytes, checksum : typing.Union[str, bytes]):
    checksum = checksum.strip()
    if isinstance(checksum, bytes):
        checksum = checksum.decode("utf-8")

    file_sha256 = hashlib.sha256(filecontent).hexdigest().upper()

    if file_sha256 == checksum.upper():
        return True
    else:
        return False
    

def is_size_within_range(file_path, target_size):
    """
    Check if the file size is within ±10% of the target size.

    :param file_path: Path to the file.
    :param target_size: Target file size in bytes.
    :return: True if the size is within the range, False otherwise.
    """
    if not os.path.exists(file_path):
        return False

    actual_size = os.path.getsize(file_path)
    margin = 0.1 * target_size  # 10% of the target size

    lower_bound = target_size - margin
    upper_bound = target_size + margin

    return lower_bound <= actual_size <= upper_bound