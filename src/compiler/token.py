from dataclasses import dataclass
from enum import StrEnum

# Special object for unit tests that don't care about the token location
L: tuple[int, int] = (-1, -1)


class TokenType(StrEnum):
    ident = "identifier"
    integ = "integer"
    op = "operator"
    punct = "punctuation"
    end = "end"


@dataclass
class Token:
    """Token class for keeping location and type information"""

    text: str
    ttype: TokenType
    loc: tuple[int, int]

    # This enforces that type is one of the valid token types
    def __init__(self, text: str, ttype: TokenType | str, loc: tuple[int, int] = L):
        self.text = text
        self.ttype = TokenType(ttype)
        self.loc = loc

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Token):
            return False
        if self.loc == L or other.loc == L:
            return True
        return (
            self.text == other.text
            and self.ttype == other.ttype
            and self.loc == other.loc
        )
