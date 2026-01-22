from dataclasses import dataclass
from enum import StrEnum


@dataclass
class Location:

    row: int
    col: int

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Location):
            return False
        if self.row == -1 or other.row == -1:
            return True
        return self.row == other.row and self.col == other.col

    def __str__(self) -> str:
        return f"({self.row}, {self.col})"


# Special object for unit tests that don't care about the token location
L: Location = Location(-1, -1)


class TokenType(StrEnum):
    ident = "identifier"
    integ = "integer"
    op = "operator"
    punct = "punctuation"
    end = "end"


@dataclass(init=False)
class Token:
    """Token class for keeping location and type information"""

    text: str
    ttype: TokenType
    loc: Location

    # This enforces that type is one of the valid token types
    def __init__(
        self,
        text: str,
        ttype: TokenType | str,
        loc: tuple[int, int] = (-1, -1),
    ):
        self.text = text
        self.ttype = TokenType(ttype)
        self.loc = Location(loc[0], loc[1])
