import re

def tokenize(source_code: str) -> list[str]:
    """Transforms source code string into a list of tokens"""
    whitespace = re.compile("[\t\n ]+")
    integer = re.compile("[0-9]+")
    identr = re.compile("[a-zA-Z_][a-zA-Z_0-9]*")
    regexes = [integer, identr]

    tokens = []
    i = 0
    total = len(source_code)

    # Iterate through the source code, matching regexes in order
    while i < total:
        # Ignore whitespace characters
        match whitespace.match(source_code, i):
            case None: pass
            case m: i = m.end()
        # Iterate through regexes
        for reg in regexes:
            match reg.match(source_code, i):
                case None: 
                    pass
                case m:
                    tokens.append(m.group())
                    i = m.end ()
                    break
        else:
            # No regex matches, then end loop
            break

    return tokens