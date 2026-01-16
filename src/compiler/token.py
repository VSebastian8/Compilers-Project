from dataclasses import dataclass
from typing import Literal

# Special object for unit tests that don't care about the token location
L: tuple[int, int] = (-1, -1) 

@dataclass
class Token:
    """Token class for keeping location and type information"""
    text: str
    ttype: str
    loc: tuple[int, int]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Token):
            return False
        if self.loc == L or other.loc == L:
            return True 
        return self.text == other.text and self.ttype == other.ttype and self.loc == other.loc