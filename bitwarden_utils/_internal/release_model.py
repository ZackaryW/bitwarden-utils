from dataclasses import dataclass
from datetime import datetime
from functools import cached_property
import os
from typing import List
import typing
from typing_extensions import TypedDict
import requests
from bitwarden_utils._internal.utils import checksum_verify

class Author(TypedDict):
    login: str
    id: int
    node_id: str
    avatar_url: str
    gravatar_id: str
    url: str
    html_url: str
    followers_url: str
    following_url: str
    gists_url: str
    starred_url: str
    subscriptions_url: str
    organizations_url: str
    repos_url: str
    events_url: str
    received_events_url: str
    type: str
    site_admin: bool

class Asset(TypedDict):
    url: str
    id: int
    node_id: str
    name: str
    label: str
    uploader: Author
    content_type: str
    state: str
    size: int
    download_count: int
    created_at: datetime
    updated_at: datetime
    browser_download_url: str


@dataclass(init=False)
class Release:
    url: str
    assets_url: str
    upload_url: str
    html_url: str
    id: int
    author: Author
    node_id: str
    tag_name: str
    target_commitish: str
    name: str
    draft: bool
    prerelease: bool
    created_at: datetime
    published_at: datetime
    assets: List[Asset]
    tarball_url: str
    zipball_url: str
    body: str
    reactions: dict = None

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if k in self.__dataclass_fields__:
                setattr(self, k, v)
            else:
                self.__dict__[k] = v

    def serialize(self):
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}

    @cached_property
    def version(self):
        return self.name.split("v")[1]

    @property
    def __local_platform(self):
        match os.name:
            case "nt":
                return "windows"
            case "posix":
                return "linux"
            case "mac":
                return "macos"
            case _:
                raise Exception("Unsupported platform")

    @cached_property
    def local_checksum(self):
        for asset in self.assets:
            if self.__local_platform in asset["name"] and asset["name"].endswith(".txt"):
                return asset["browser_download_url"]
   
    @cached_property
    def local_download(self):
        for asset in self.assets:
            if self.__local_platform in asset["name"] and asset["name"].endswith(".zip"):
                return asset["browser_download_url"]

    def download(
        self, 
        platform : typing.Literal["windows", "linux", "macos"] = None,
        verify_on_download : bool = True
    ):
        platform = platform or self.__local_platform
        download_url = None
        for asset in self.assets:
            if platform in asset["name"] and asset["name"].endswith(".zip"):
                download_url =  asset["browser_download_url"]
                break
        
        checksum_url = None
        for asset in self.assets:
            if platform in asset["name"] and asset["name"].endswith(".txt"):
                return asset["browser_download_url"]

        if download_url is None or checksum_url is None:
            raise Exception("Download url or checksum url not found")
        
        zip_res = requests.get(download_url)
        txt_res = requests.get(checksum_url)

        downloadContent = zip_res.content
        checksumContent = txt_res.content.strip().decode("utf-8")

        if verify_on_download and checksum_verify(downloadContent, checksumContent):
            return downloadContent, checksumContent
        else:
            raise Exception("Checksum verification failed")

    def extractTo(
        self, 
        folder : str, 
        platform : typing.Literal["windows", "linux", "macos"] = None
    ):
        download, _ = self.download(platform)

        import zipfile
        with zipfile.ZipFile(download, 'r') as zip_ref:
            zip_ref.extractall(folder)
