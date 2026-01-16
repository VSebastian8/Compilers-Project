import re
from compiler.token import Token

def tokenize(source_code: str) -> list[Token]:
    """Transforms source code string into a list of tokens"""
    whitespace = re.compile("[\t\n ]+")
    integer = re.compile("[0-9]+")
    identr = re.compile("[a-zA-Z_][a-zA-Z_0-9]*")
    regexes = [(integer, "integer"), (identr, "identifier")]

    tokens = []
    i = 0
    total = len(source_code)
    row = 0
    col = 0

    # Iterate through the source code, matching regexes in order
    while i < total:
        # Ignore whitespace characters
        match whitespace.match(source_code, i):
            case None: pass
            case m: 
                i = m.end()
                for ch in m.group():
                    if ch == '\n':
                        row += 1
                        col = 0
                    else:
                        col += 1
        # Iterate through regexes
        for [reg, ttype] in regexes:
            match reg.match(source_code, i):
                case None: 
                    pass
                case m:
                    tokens.append(Token(m.group(), ttype, (row, col)))
                    i = m.end ()
                    col += len(m.group())
                    break
        else:
            # No regex matches, then end loop
            break

    return tokens