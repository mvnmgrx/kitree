"""???

Author:
    (C) Marvin Mager - @mvnmgrx - 2022

License identifier:
    GPL-3.0
"""

from dataclasses import dataclass

@dataclass
class Credentials():
    """Simple credential store"""

    id: str = ""
    """Identifier of the credential"""

    username: str = ""
    """The username to use for login"""

    password: str = ""
    """The password to use for login"""

    domain: str = ""
    """The domain to authenticate to"""

@dataclass
class KnownProject():
    """A project known to kitree"""

    name: str = ""
    """Name of the project"""

    path: str = ""
    """Path to the project"""
