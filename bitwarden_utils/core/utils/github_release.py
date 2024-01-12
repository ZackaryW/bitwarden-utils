
from typing import TypedDict
import typing

from pydantic import BaseModel

class Asset(TypedDict):
    url: str
    id: int
    node_id: str
    name: str
    label: str
    content_type: str
    state: str
    size: int
    download_count: int
    browser_download_url: str

class Release(BaseModel):
    model_config = {
        "extra" : "allow"
    }
    
    url: str
    assets_url: str
    upload_url: str
    html_url: str
    id: int
    node_id: str
    tag_name: str
    target_commitish: str
    name: str
    draft: bool
    prerelease: bool
    assets: typing.List[Asset]
    tarball_url: str
    zipball_url: str
    body: str