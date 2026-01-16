from compiler.token import Token, L
from compiler.tokenizer import tokenize


def test_tokenizer_basics() -> None:
    # Whitespace test
    assert tokenize("  \n \t \n\n\n\n  ") == []
    # Row and Column test
    assert tokenize("  if  3\nwhile") == [
        Token("if", "identifier", (0, 2)),
        Token("3", "integer", (0, 6)),
        Token("while", "identifier", (1, 0)),
    ]
    # L object test
    assert tokenize("  if  x12 321\tbreak") == [
        Token("if", "identifier", L),
        Token("x12", "identifier", L),
        Token("321", "integer", L),
        Token("break", "identifier", L),
    ]


def test_tokenizer_op_punct() -> None:
    assert tokenize("x == y") == [
        Token("x", "identifier", (0, 0)),
        Token("==", "operator", (0, 2)),
        Token("y", "identifier", (0, 5)),
    ]
    assert tokenize("(<=)*+!=;") == [
        Token("(", "punctuation", (0, 0)),
        Token("<=", "operator", (0, 1)),
        Token(")", "punctuation", (0, 3)),
        Token("*", "operator", (0, 4)),
        Token("+", "operator", (0, 5)),
        Token("!=", "operator", (0, 6)),
        Token(";", "punctuation", (0, 8)),
    ]
    assert tokenize("( first , second_1 < second_2) \n\n }472{") == [
        Token("(", "punctuation", (0, 0)),
        Token("first", "identifier", (0, 2)),
        Token(",", "punctuation", (0, 8)),
        Token("second_1", "identifier", (0, 10)),
        Token("<", "operator", (0, 19)),
        Token("second_2", "identifier", (0, 21)),
        Token(")", "punctuation", (0, 29)),
        Token("}", "punctuation", (2, 1)),
        Token("472", "integer", (2, 2)),
        Token("{", "punctuation", (2, 5)),
    ]


def test_tokenizer_comments() -> None:
    # Single line
    assert tokenize("// bla bla \n while (True) {\n\tx = y * 2;\n } # bla123 \n") == [
        Token("while", "identifier", L),
        Token("(", "punctuation", L),
        Token("True", "identifier", (1, 8)),
        Token(")", "punctuation"),
        Token("{", "punctuation"),
        Token("x", "identifier"),
        Token("=", "operator"),
        Token("y", "identifier"),
        Token("*", "operator"),
        Token("2", "integer"),
        Token(";", "punctuation"),
        Token("}", "punctuation", (3, 1)),
    ]
    # Multi line
    assert tokenize("/* hey */") == []
    assert tokenize("before /* \n multi \n line\ncomment */ after") == [
        Token("before", "identifier", (0, 0)),
        Token("after", "identifier", (3, 11)),
    ]
