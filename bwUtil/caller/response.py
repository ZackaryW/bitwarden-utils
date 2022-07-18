from dataclasses import dataclass
import functools
import typing
import re
from functools import cached_property


@dataclass(frozen=True)
class BwResponse:
    """
    a wrapper of subprocess response

    ideally functions such as login_not_logged_in and session_extract should not be part of the methods in this class
    currently, this is done to have less classes

    """

    raw : str

    @cached_property
    def rawLines(self) -> typing.List[str]:
        """ 
        split the raw response into lines

        Returns:
            typing.List[str]
        """

        return self.raw.split("/n")

    @cached_property
    def login_not_logged_in(self):
        """
        it will check against of the lines matching the regexp "login not logged in" 

        Returns:
            bool: True if not logged in 
        """

        return any(["You are not logged in." in line for line in self.rawLines]) 

    @cached_property
    def login_is_logged_in(self):
        """
        it will check against of the lines matching the regexp `"You are already logged in as {email}"`
        and extract the email from the line

        Returns:
            str: email if logged in else None
        """

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
        """
        it will extract the session from the raw response

        Returns:
            str: session if present else None
        """

        if "$ export BW_SESSION" not in self.raw:
            return None
        try:
            for line in self.rawLines:
                if "$ export BW_SESSION" in line:
                    eline = line.split("=", 1)[1].strip('"').split('"')[0]
                    return eline
        except:
            return None

    def __str__(self):
        return self.raw