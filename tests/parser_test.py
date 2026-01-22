from compiler.parser import parse
from compiler.token import Token, L
from compiler.ast import (
    Literal,
    Identifier,
    UnaryOp,
    BinaryOp,
    IfThenElse,
    FunctionCall,
    Assignment,
    Block,
    While,
)
from compiler.tokenizer import tokenize


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

    assert parse(tokenize("x + y == 2 or x < 1 + y / 2")) == BinaryOp(
        BinaryOp(BinaryOp(Identifier("x"), "+", Identifier("y")), "==", Literal(2)),
        "or",
        BinaryOp(
            Identifier("x"),
            "<",
            BinaryOp(
                Literal(1),
                "+",
                BinaryOp(Identifier("y"), "/", Literal(2)),
            ),
        ),
    )

    assert parse(tokenize("not not x")) == UnaryOp(
        "not", UnaryOp("not", Identifier("x"))
    )

    assert parse(tokenize("-1 + 2 != 3")) == BinaryOp(
        BinaryOp(UnaryOp("-", Literal(1)), "+", Literal(2)), "!=", Literal(3)
    )

    assert parse(tokenize("x * -1")) == BinaryOp(
        Identifier("x"), "*", UnaryOp("-", Literal(1))
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
        match=re.escape("(0, 2): unexpected token EOF"),
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

    # Assignment to non-identifier
    with pytest.raises(Exception, match=re.escape("(0, 3): unexpected token =")):
        parse(tokenize("27 = x"))

    # Assignment to non-identifier (b * 3 = c makes no sense)
    with pytest.raises(Exception, match=re.escape("(0, 10): unexpected token =")):
        parse(tokenize("a = b * 3 = c"))

    # Block statements without ;
    with pytest.raises(Exception, match=re.escape("(0, 4): missing ;")):
        parse(tokenize("{ x y }"))

    with pytest.raises(Exception, match=re.escape("(0, 23): missing ;")):
        parse(tokenize("{ if true then { a } b c }"))


def test_parser_if_then_else() -> None:
    # if a then b + c else x * y
    assert parse(
        [
            Token("if", "identifier", L),
            Token("a", "identifier", L),
            Token("then", "identifier", L),
            Token("b", "identifier", L),
            Token("+", "operator", L),
            Token("c", "identifier", L),
            Token("else", "identifier", L),
            Token("x", "identifier", L),
            Token("*", "operator", L),
            Token("y", "identifier", L),
        ]
    ) == IfThenElse(
        Identifier("a"),
        BinaryOp(Identifier("b"), "+", Identifier("c")),
        BinaryOp(Identifier("x"), "*", Identifier("y")),
    )

    # if x + 2 * 2 then True
    assert parse(
        [
            Token("if", "identifier", L),
            Token("x", "identifier", L),
            Token("+", "operator", L),
            Token("2", "integer", L),
            Token("*", "operator", L),
            Token("2", "integer", L),
            Token("then", "identifier", L),
            Token("True", "identifier", L),
        ]
    ) == IfThenElse(
        BinaryOp(Identifier("x"), "+", BinaryOp(Literal(2), "*", Literal(2))),
        Identifier("True"),
        None,
    )

    # 5 * if x then if y then 2 else 3
    assert parse(
        [
            Token("5", "integer", L),
            Token("*", "operator", L),
            Token("if", "identifier", L),
            Token("x", "identifier", L),
            Token("then", "identifier", L),
            Token("if", "identifier", L),
            Token("y", "identifier", L),
            Token("then", "identifier", L),
            Token("2", "integer", L),
            Token("else", "identifier", L),
            Token("3", "integer", L),
        ]
    ) == BinaryOp(
        Literal(5),
        "*",
        IfThenElse(
            Identifier("x"),
            IfThenElse(Identifier("y"), Literal(2), Literal(3)),
            None,
        ),
    )


def test_parser_functions() -> None:
    assert parse(tokenize("f(x, y + z)")) == FunctionCall(
        "f", [Identifier("x"), BinaryOp(Identifier("y"), "+", Identifier("z"))]
    )

    assert parse(tokenize("print_int(27)")) == FunctionCall("print_int", [Literal(27)])

    assert parse(tokenize("main()")) == FunctionCall("main", [])


def test_parser_assignment() -> None:
    assert parse(tokenize("x = 24")) == Assignment("x", Literal(24))

    assert parse(tokenize("a = b = c = (d + 2)")) == Assignment(
        "a",
        Assignment(
            "b",
            Assignment("c", BinaryOp(Identifier("d"), "+", Literal(2))),
        ),
    )

    assert parse(tokenize("if True then x = y == 12 or 300 > z * 2")) == IfThenElse(
        Identifier("True"),
        Assignment(
            "x",
            BinaryOp(
                BinaryOp(Identifier("y"), "==", Literal(12)),
                "or",
                BinaryOp(Literal(300), ">", BinaryOp(Identifier("z"), "*", Literal(2))),
            ),
        ),
        None,
    )

    assert parse(tokenize("2 * (hello = world)")) == BinaryOp(
        Literal(2), "*", Assignment("hello", Identifier("world"))
    )


def test_parser_block() -> None:
    assert parse(tokenize("{ x = y * 2 }")) == Block(
        [Assignment("x", BinaryOp(Identifier("y"), "*", Literal(2)))]
    )

    assert parse(tokenize("{ x = 2; 3 + 3 / 3; f(x); }")) == Block(
        [
            Assignment("x", Literal(2)),
            BinaryOp(Literal(3), "+", BinaryOp(Literal(3), "/", Literal(3))),
            FunctionCall("f", [Identifier("x")]),
            Literal(None),
        ]
    )

    assert parse(tokenize("while True do { print_int(14); }")) == While(
        Identifier("True"),
        Block([FunctionCall("print_int", [Literal(14)]), Literal(None)]),
    )

    assert (
        parse(
            tokenize(
                """
        {
            while f() do {
                x = 10;
                y = if g(x) then {
                    x = x + 1;
                    x
                } else {
                    g(x)
                };  # <-- (this semicolon will become optional later)
                g(y);
            };  # <------ (this too)
            123
        }"""
            )
        )
        == Block(
            [
                While(
                    FunctionCall("f", []),
                    Block(
                        [
                            Assignment("x", Literal(10)),
                            Assignment(
                                "y",
                                IfThenElse(
                                    FunctionCall("g", [Identifier("x")]),
                                    Block(
                                        [
                                            Assignment(
                                                "x",
                                                BinaryOp(
                                                    Identifier("x"), "+", Literal(1)
                                                ),
                                            ),
                                            Identifier("x"),
                                        ]
                                    ),
                                    Block([FunctionCall("g", [Identifier("x")])]),
                                ),
                            ),
                            FunctionCall("g", [Identifier("y")]),
                            Literal(None),
                        ]
                    ),
                ),
                Literal(123),
            ]
        )
    )

    assert parse(tokenize("x = { { f(a) } { b } }")) == Assignment(
        "x",
        Block(
            [Block([FunctionCall("f", [Identifier("a")])]), Block([Identifier("b")])]
        ),
    )

    assert (
        parse(tokenize("{ { x } { y } }"))
        == parse(tokenize("{ { x }; { y } }"))
        != parse(tokenize("{ { x }; { y }; }"))
    )

    assert parse(tokenize("{ if true then { a } else { b } c }")) == parse(
        tokenize("{ if true then { a } else { b }; c }")
    )
