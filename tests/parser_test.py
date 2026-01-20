from compiler.parser import parse
from compiler.token import Token, L
from compiler.ast import Identifier, BinaryOp, Literal


def test_parser_basics() -> None:
    # 23 + 5
    assert parse(
        [
            Token("23", "integer", L),
            Token("+", "operator", L),
            Token("5", "integer", L),
        ]
    ) == BinaryOp(Literal(23), "+", Literal(5))

    # x / 2
    assert parse(
        [
            Token("x", "identifier", L),
            Token("/", "operator", L),
            Token("2", "integer", L),
        ]
    ) == BinaryOp(Identifier("x"), "/", Literal(2))


def test_parser_associativity() -> None:
    # 1 + 2 - 3
    assert parse(
        [
            Token("1", "integer", L),
            Token("+", "operator", L),
            Token("2", "integer", L),
            Token("-", "operator", L),
            Token("3", "integer", L),
        ]
    ) == BinaryOp(BinaryOp(Literal(1), "+", Literal(2)), "-", Literal(3))

    # x / y * z
    assert parse(
        [
            Token("x", "identifier", L),
            Token("/", "operator", L),
            Token("y", "identifier", L),
            Token("*", "operator", L),
            Token("z", "identifier", L),
        ]
    ) == BinaryOp(BinaryOp(Identifier("x"), "/", Identifier("y")), "*", Identifier("z"))


def test_parser_precedence() -> None:
    # 1 + 1 / x
    assert parse(
        [
            Token("1", "integer", L),
            Token("+", "operator", L),
            Token("1", "integer", L),
            Token("/", "operator", L),
            Token("x", "identifier", L),
        ]
    ) == BinaryOp(Literal(1), "+", BinaryOp(Literal(1), "/", Identifier("x")))

    # 2 + x * x / 2 - 2 * hello
    assert parse(
        [
            Token("2", "integer", L),
            Token("+", "operator", L),
            Token("x", "identifier", L),
            Token("*", "operator", L),
            Token("x", "identifier", L),
            Token("/", "operator", L),
            Token("2", "integer", L),
            Token("-", "operator", L),
            Token("2", "integer", L),
            Token("*", "operator", L),
            Token("hello", "identifier", L),
        ]
    ) == BinaryOp(
        left=BinaryOp(
            left=Literal(2),
            op="+",
            right=BinaryOp(
                BinaryOp(Identifier("x"), "*", Identifier("x")), "/", Literal(2)
            ),
        ),
        op="-",
        right=BinaryOp(Literal(2), "*", Identifier("hello")),
    )


def test_parser_parentheses() -> None:
    # 2026 * (x + y)
    assert parse(
        [
            Token("2026", "integer", L),
            Token("*", "operator", L),
            Token("(", "punctuation", L),
            Token("x", "identifier", L),
            Token("+", "operator", L),
            Token("y", "identifier", L),
            Token(")", "punctuation", L),
        ]
    ) == BinaryOp(Literal(2026), "*", BinaryOp(Identifier("x"), "+", Identifier("y")))

    # 2026 * (((((x - y)))))
    assert parse(
        [
            Token("2026", "integer", L),
            Token("*", "operator", L),
            Token("(", "punctuation", L),
            Token("(", "punctuation", L),
            Token("(", "punctuation", L),
            Token("(", "punctuation", L),
            Token("(", "punctuation", L),
            Token("x", "identifier", L),
            Token("-", "operator", L),
            Token("y", "identifier", L),
            Token(")", "punctuation", L),
            Token(")", "punctuation", L),
            Token(")", "punctuation", L),
            Token(")", "punctuation", L),
            Token(")", "punctuation", L),
        ]
    ) == BinaryOp(Literal(2026), "*", BinaryOp(Identifier("x"), "-", Identifier("y")))

    # (x) * (3 - 1 / (y * 15))
    assert parse(
        [
            Token("(", "punctuation", L),
            Token("x", "identifier", L),
            Token(")", "punctuation", L),
            Token("*", "operator", L),
            Token("(", "punctuation", L),
            Token("3", "integer", L),
            Token("-", "operator", L),
            Token("1", "integer", L),
            Token("/", "operator", L),
            Token("(", "punctuation", L),
            Token("y", "identifier", L),
            Token("*", "operator", L),
            Token("15", "integer", L),
            Token(")", "punctuation", L),
            Token(")", "punctuation", L),
        ]
    ) == BinaryOp(
        Identifier("x"),
        "*",
        BinaryOp(
            Literal(3),
            "-",
            BinaryOp(Literal(1), "/", BinaryOp(Identifier("y"), "*", Literal(15))),
        ),
    )


def test_parser_exceptions() -> None:
    import pytest, re

    # No input
    with pytest.raises(Exception, match="Empty list of tokens"):
        parse([])

    # Leftover text:
    # 3 4
    with pytest.raises(Exception, match=re.escape("(0, 2): unexpected token 4")):
        parse(
            [
                Token("3", "integer", L),
                Token("4", "integer", (0, 2)),
            ]
        )

    # Unfinished expression
    # x +
    with pytest.raises(
        Exception,
        match=re.escape('(0, 2): expected "(", an integer literal or an identifier'),
    ):
        parse(
            [
                Token("x", "identifier", L),
                Token("+", "operator", (0, 2)),
            ]
        )

    # Not matching parentheses
    # x + (21 + 5
    with pytest.raises(
        Exception,
        match=re.escape('(0, 10): expected ")"'),
    ):
        parse(
            [
                Token("x", "identifier", (0, 0)),
                Token("+", "operator", (0, 2)),
                Token("(", "punctuation", (0, 4)),
                Token("21", "integer", (0, 5)),
                Token("+", "operator", (0, 8)),
                Token("5", "integer", (0, 10)),
            ]
        )
