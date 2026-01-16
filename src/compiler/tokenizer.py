import re
from compiler.token import Token, TokenType


def tokenize(source_code: str) -> list[Token]:
    """Transforms source code string into a list of tokens"""
    whitespace = re.compile(r"[\t\n ]+")
    line_comment = re.compile("(#|//)(.*)\n")
    multi_line_comment = re.compile("(/\\*)(.|\n)*(\\*/)")
    r_int = re.compile(r"[0-9]+")
    r_ident = re.compile(r"[a-zA-Z_][a-zA-Z_0-9]*")
    r_op = re.compile(r"<=|>=|==|!=|<|>|=|\+|-|\*|/|%")
    r_punct = re.compile(r"\(|\)|\{|\}|\,|;")

    regexes = [
        (r_int, TokenType.integ),
        (r_ident, TokenType.ident),
        (r_op, TokenType.op),
        (r_punct, TokenType.punct),
    ]
    tokens = []
    i = 0
    total = len(source_code)
    row = 0
    col = 0

    # Iterate through the source code, matching regexes in order
    while i < total:
        # Ignore whitespace characters
        match whitespace.match(source_code, i):
            case None:
                pass
            case m:
                i = m.end()
                for ch in m.group():
                    if ch == "\n":
                        row += 1
                        col = 0
                    else:
                        col += 1
        # Ignore line comments
        match line_comment.match(source_code, i):
            case None:
                pass
            case m:
                i = m.end()
                row += 1
                col = 0
                continue
        # Ignore multi-line comments
        match multi_line_comment.match(source_code, i):
            case None:
                pass
            case m:
                i = m.end()
                for ch in m.group():
                    if ch == "\n":
                        row += 1
                        col = 0
                    else:
                        col += 1
                continue
        # Iterate through regexes
        for [reg, ttype] in regexes:
            match reg.match(source_code, i):
                case None:
                    pass
                case m:
                    tokens.append(Token(m.group(), ttype, (row, col)))
                    i = m.end()
                    col += len(m.group())
                    break
        else:
            # No regex matches, then end loop
            break

    return tokens
