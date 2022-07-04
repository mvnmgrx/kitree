"""???

Author:
    (C) Marvin Mager - @mvnmgrx - 2022

License identifier:
    GPL-3.0
"""

from dataclasses import dataclass

@dataclass
class Credentials():
    Username: str = ""
    Password: str = ""
    Domain: str = ""