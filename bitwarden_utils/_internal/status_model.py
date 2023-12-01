
import typing
from typing_extensions import TypedDict


class Status(TypedDict):
    serverUrl : typing.Optional[str]
    lastSync : typing.Optional[str]
    userEmail : typing.Optional[str]
    userId : typing.Optional[str]
    status : typing.Literal["locked", "unlocked"]