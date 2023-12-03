
import typing
from typing_extensions import TypedDict
from pydantic import BaseModel, ConfigDict, Field

class Status(TypedDict):
    serverUrl : typing.Optional[str]
    lastSync : typing.Optional[str]
    userEmail : typing.Optional[str]
    userId : typing.Optional[str]
    status : typing.Literal["locked", "unlocked", "unauthenticated"]


class Attachment(TypedDict):
    id : str
    fileName : str
    size : int
    sizeName : str
    url : str


class Item(BaseModel):
    id : str
    organizationId: typing.Optional[str] = None
    folderId : typing.Optional[str] = None
    type : int
    reprompt : int
    name : str
    notes : typing.Optional[str] = None
    favorite : bool = False
    fields : typing.List[dict] = Field(default_factory=list)
    login : dict = Field(default_factory=dict)
    collectionIds : typing.List[str] = Field(default_factory=list)
    revisionDate : str
    creationDate : str
    deletedDate : typing.Optional[str] = None

    attachments : typing.Optional[typing.List[Attachment]] = None

    model_config = ConfigDict(
        extra="allow",
    )