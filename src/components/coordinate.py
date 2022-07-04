"""???

Author:
    (C) Marvin Mager - @mvnmgrx - 2022

License identifier:
    GPL-3.0
"""

from dataclasses import dataclass

@dataclass(frozen=True)
class Coordinate():
    x: int = 0
    y: int = 0
    z: int = 0