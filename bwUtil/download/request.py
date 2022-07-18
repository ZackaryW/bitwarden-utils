from io import BytesIO
import os
import typing
import requests
import hashlib
import zipfile

def _downloadUrlMatch(assets, starts_with : str, ends_with : str):
    """
    this method will find the download url that matches the given parameters
    """

    for asset in assets:
        download_link :str = asset["browser_download_url"]
        download_filename = download_link.rsplit("/", 1)[1]
        if download_filename.startswith(starts_with) and download_filename.endswith(ends_with):
            return download_link

def downloadCli(platform : typing.Literal["windows", "linux", "macos"], destination : str, verify : bool = True):
    """
    this method will download the latest version of bitwarden cli and verifies it if verify is True

    Args:
        platform: the platform to download the cli for
        destination (str): the path to download the cli to
        verify (bool, optional): Defaults to True. if True, the cli will be verified
    """

    if not os.path.isdir(destination):
        raise Exception("Destination is not a directory")

    if not os.path.exists(destination):
        os.makedirs(destination, exist_ok=True)

    # parsing through github releases

    baseurl = "https://api.github.com/repos/bitwarden/clients/releases"
    res = requests.get(baseurl)
    if res.status_code != 200:
        raise Exception("Could not get latest release from github")

    data = res.json()
    for asset in data:
        if not asset["name"].startswith("CLI"):
            continue
        CliAssets = asset["assets"]
        break
    
    # extract download links
    if (downloadUrl := _downloadUrlMatch(CliAssets, f"bw-{platform}", ".zip")) is None:
        raise Exception("Could not find download link")

    if verify and (checkSumUrl := _downloadUrlMatch(CliAssets, f"bw-{platform}-sha256", ".txt")) is None:
        raise Exception("Could not find checksum link")
    
    download_res = requests.get(downloadUrl)

    if verify:
        download_checksum_res = requests.get(checkSumUrl)

    if download_res.status_code != 200:
        raise Exception("Could not download latest release from github")

    if verify and download_checksum_res.status_code != 200:    
        raise Exception("Could not download checksum from github")

    downloadContent = download_res.content

    if verify:
        checsumContent = download_checksum_res.content.strip().decode("utf-8")

        # downloadcontent generate sha256
        file_sha256 = hashlib.sha256(downloadContent).hexdigest().upper()

        if file_sha256 != checsumContent:
            raise Exception("Checksum does not match")

    with zipfile.ZipFile(BytesIO(downloadContent)) as zip_file:
        zip_file.extractall(destination)
