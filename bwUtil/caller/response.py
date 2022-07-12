from dataclasses import dataclass
import functools
import typing
import re
from functools import cached_property


@dataclass(frozen=True)
class BwResponse:
    raw : typing.List[str]

    @cached_property
    def login_not_logged_in(self):
        return any(["You are not logged in." in line for line in self.raw]) 

    @cached_property
    def login_is_logged_in(self):
        # You are already logged in as {email}.
        # extract email from raw
        try:
            email_regex = re.compile(r"You are already logged in as (?P<email>.*).")
            email = email_regex.search(self.raw[0]).group("email")
            return email
        except:
            return None

    def __str__(self):
        return "\n".join(self.raw)