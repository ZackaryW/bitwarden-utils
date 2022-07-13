from dataclasses import dataclass
import functools
import typing
import re
from functools import cached_property


@dataclass(frozen=True)
class BwResponse:
    raw : str

    @cached_property
    def rawLines(self):
        return self.raw.split("/n")

    @cached_property
    def login_not_logged_in(self):
        return any(["You are not logged in." in line for line in self.rawLines]) 

    @cached_property
    def login_is_logged_in(self):
        # You are already logged in as {email}.
        # extract email from raw
        try:
            email_regex = re.compile(r"You are already logged in as (?P<email>.*).")
            email = email_regex.search(self.rawLines[0]).group("email")
            return email
        except:
            return None

    @cached_property
    def session_extract(self):
        if "$ export BW_SESSION" not in self.raw:
            return None
        try:
            for line in self.rawLines:
                if "$ export BW_SESSION" in line:
                    return line.split("=", 1)[1].strip('"')
        except:
            return None

    def __str__(self):
        return self.raw