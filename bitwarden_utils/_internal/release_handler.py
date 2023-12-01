
import datetime
import os
from time import sleep
import typing
from pydantic import BaseModel, Field
import requests
from bitwarden_utils._internal.intact_json import JsonChecksumHandler
from bitwarden_utils._internal.release_model import Release
from bitwarden_utils.cache import DIR

class ReleaseCollectionModel(BaseModel):
    paged : typing.Dict[int, typing.List[str]] = Field(default_factory=dict)
    lastModifed : datetime.date = Field(default_factory=lambda: datetime.datetime.now().date())
    releases : typing.Dict[str, Release] = Field(default_factory=dict)

class ReleaseHandler:
    __URL : str = "https://api.github.com/repos/bitwarden/clients/releases"
    __model : ReleaseCollectionModel
    __handler : JsonChecksumHandler

    MAX_DEPTH : int =20

    def __init__(self, path : str):
        self.__handler = JsonChecksumHandler(path)
        self.__model = ReleaseCollectionModel(**self.__handler.read_json())
        self.refresh()
            
    def refresh(self):
        if datetime.datetime.now().date() > self.__model.lastModifed:
            self.__model.paged = {}
            self.__model.lastModifed = datetime.datetime.now().date()
            self.__paged_history = {}
            self.__handler.update_json(self.__model.model_dump())
    
    def get_releases(self, page : int =1) -> typing.List[Release]:
        if page < 0:
            raise ValueError("page cannot be less than 0")
        
        if page in self.__paged_history:
            return self.__paged_history[page]

        if page in self.__model.paged:
            self.__paged_history[page] = [self.__model.releases[r] for r in self.__model.paged[page]]
            return self.__paged_history[page]

        res = requests.get(self.__URL, params={"page": page})
        data = res.json()
        releases : typing.List[Release] = []

        for release in data:
            self.__model.releases[release["url"]] =Release(**release)

        self.__handler.update_json(self.__model.model_dump())

        return releases
    
    def get_release_version(self, version : str):
        # if not 2 . in version
        if "." not in version:
            return None
        
        splitted = version.split(".")

        if len(splitted) != 3:
            return None

        syear, smonth, sv = splitted
        syear, smonth = int(syear), int(smonth)

        counter = 1

        
        while True:
            if counter > self.MAX_DEPTH:
                return None

            curr_page_releases = self.get_releases(counter)

            for release in curr_page_releases:
                if release.version == version:
                    return release

            dyear, dmonth, dv = release.version.split(".")
            dyear, dmonth = int(dyear), int(dmonth)

            if dyear > syear or (dyear == syear and dmonth < smonth):
                return None
                
            counter += 1

            sleep(1)

    def get_latest_version(self):
        counter = 1
        while True:
            if counter > self.MAX_DEPTH:
                return None

            releases = self.get_releases(1)
            if len(releases) != 0:
                return releases[0]

            counter += 1
            sleep(1)
                
GLOBAL_RELEASE_HANDLER = ReleaseHandler(os.path.join(DIR, "repos"))
