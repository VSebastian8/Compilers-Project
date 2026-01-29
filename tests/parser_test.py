from compiler.parser import parse
from compiler.token import Token
from compiler.ast import (
    Literal,
    Identifier,
    UnaryOp,
    BinaryOp,
    IfThenElse,
    FunctionCall,
    Assignment,
    VarDec,
    Block,
    While,
    LoopControl,
    Module,
)
from compiler.tokenizer import tokenize
from compiler.types import Int, Bool, Unit, FunType


def test_parser_basics() -> None:
    # 23 + 5
    assert parse(
        [
            Token("23", "integer"),
            Token("+", "operator"),
            Token("5", "integer"),
        ]
    ) == Module([], [BinaryOp(Literal(23), "+", Literal(5))])

    # x / 2
    assert parse(
        [
            Token("x", "identifier"),
            Token("/", "operator"),
            Token("2", "integer"),
        ]
    ) == Module([], [BinaryOp(Identifier("x"), "/", Literal(2))])


def test_parser_associativity() -> None:
    # 1 + 2 - 3
    assert parse(
        [
            Token("1", "integer"),
            Token("+", "operator"),
            Token("2", "integer"),
            Token("-", "operator"),
            Token("3", "integer"),
        ]
    ) == Module([], [BinaryOp(BinaryOp(Literal(1), "+", Literal(2)), "-", Literal(3))])

    # x / y * z
    assert parse(
        [
            Token("x", "identifier"),
            Token("/", "operator"),
            Token("y", "identifier"),
            Token("*", "operator"),
            Token("z", "identifier"),
        ]
    ) == Module(
        [],
        [
            BinaryOp(
                BinaryOp(Identifier("x"), "/", Identifier("y")), "*", Identifier("z")
            )
        ],
    )


def test_parser_precedence() -> None:
    # 1 + 1 / x
    assert parse(
        [
            Token("1", "integer"),
            Token("+", "operator"),
            Token("1", "integer"),
            Token("/", "operator"),
            Token("x", "identifier"),
        ]
    ) == Module(
        [], [BinaryOp(Literal(1), "+", BinaryOp(Literal(1), "/", Identifier("x")))]
    )

    # 2 + x * x / 2 - 2 * hello
    assert parse(
        [
            Token("2", "integer"),
            Token("+", "operator"),
            Token("x", "identifier"),
            Token("*", "operator"),
            Token("x", "identifier"),
            Token("/", "operator"),
            Token("2", "integer"),
            Token("-", "operator"),
            Token("2", "integer"),
            Token("*", "operator"),
            Token("hello", "identifier"),
        ]
    ) == Module(
        [],
        [
            BinaryOp(
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
        ],
    )

    assert parse(tokenize("x + y == 2 or x < 1 + y / 2")) == Module(
        [],
        [
            BinaryOp(
                BinaryOp(
                    BinaryOp(Identifier("x"), "+", Identifier("y")), "==", Literal(2)
                ),
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
        ],
    )

    assert parse(tokenize("not not x")) == Module(
        [], [UnaryOp("not", UnaryOp("not", Identifier("x")))]
    )

    assert parse(tokenize("-1 + 2 != 3")) == Module(
        [],
        [
            BinaryOp(
                BinaryOp(UnaryOp("-", Literal(1)), "+", Literal(2)), "!=", Literal(3)
            )
        ],
    )

    assert parse(tokenize("x * -1")) == Module(
        [], [BinaryOp(Identifier("x"), "*", UnaryOp("-", Literal(1)))]
    )


def test_parser_parentheses() -> None:
    # 2026 * (x + y)
    assert parse(
        [
            Token("2026", "integer"),
            Token("*", "operator"),
            Token("(", "punctuation"),
            Token("x", "identifier"),
            Token("+", "operator"),
            Token("y", "identifier"),
            Token(")", "punctuation"),
        ]
    ) == Module(
        [],
        [BinaryOp(Literal(2026), "*", BinaryOp(Identifier("x"), "+", Identifier("y")))],
    )

    # 2026 * (((((x - y)))))
    assert parse(
        [
            Token("2026", "integer"),
            Token("*", "operator"),
            Token("(", "punctuation"),
            Token("(", "punctuation"),
            Token("(", "punctuation"),
            Token("(", "punctuation"),
            Token("(", "punctuation"),
            Token("x", "identifier"),
            Token("-", "operator"),
            Token("y", "identifier"),
            Token(")", "punctuation"),
            Token(")", "punctuation"),
            Token(")", "punctuation"),
            Token(")", "punctuation"),
            Token(")", "punctuation"),
        ]
    ) == Module(
        [],
        [BinaryOp(Literal(2026), "*", BinaryOp(Identifier("x"), "-", Identifier("y")))],
    )

    # (x) * (3 - 1 / (y * 15))
    assert parse(
        [
            Token("(", "punctuation"),
            Token("x", "identifier"),
            Token(")", "punctuation"),
            Token("*", "operator"),
            Token("(", "punctuation"),
            Token("3", "integer"),
            Token("-", "operator"),
            Token("1", "integer"),
            Token("/", "operator"),
            Token("(", "punctuation"),
            Token("y", "identifier"),
            Token("*", "operator"),
            Token("15", "integer"),
            Token(")", "punctuation"),
            Token(")", "punctuation"),
        ]
    ) == Module(
        [],
        [
            BinaryOp(
                Identifier("x"),
                "*",
                BinaryOp(
                    Literal(3),
                    "-",
                    BinaryOp(
                        Literal(1), "/", BinaryOp(Identifier("y"), "*", Literal(15))
                    ),
                ),
            )
        ],
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
                Token("3", "integer"),
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
                Token("x", "identifier"),
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

    # if no then
    with pytest.raises(Exception, match=re.escape('(0, 5): expected "then"')):
        parse(tokenize("{ if true"))

    # var in wrong place
    with pytest.raises(
        Exception,
        match=re.escape("(0, 21): variable declaration only allowed inside blocks"),
    ):
        parse(tokenize("if whatever then var x = 3"))

    # literal after var
    with pytest.raises(
        Exception,
        match=re.escape('(0, 6): expected identifier after var, found "2"'),
    ):
        parse(tokenize("var 2 = 3"))

    # wrong type decl
    with pytest.raises(
        Exception,
        match=re.escape('(0, 7): expected type, found "String"'),
    ):
        parse(tokenize("var x: String = hey"))

        # wrong type decl
    with pytest.raises(
        Exception,
        match=re.escape('(0, 16): expected "="'),
    ):
        parse(tokenize("var almost: Int => Int = print_int"))

        # wrong type decl
    with pytest.raises(
        Exception,
        match=re.escape('(0, 18): extra "," found'),
    ):
        parse(tokenize("var almost: (Int, ) => Unit = print_int"))


def test_parser_if_then_else() -> None:
    # if a then b + c else x * y
    assert parse(
        [
            Token("if", "identifier"),
            Token("a", "identifier"),
            Token("then", "identifier"),
            Token("b", "identifier"),
            Token("+", "operator"),
            Token("c", "identifier"),
            Token("else", "identifier"),
            Token("x", "identifier"),
            Token("*", "operator"),
            Token("y", "identifier"),
        ]
    ) == Module(
        [],
        [
            IfThenElse(
                Identifier("a"),
                BinaryOp(Identifier("b"), "+", Identifier("c")),
                BinaryOp(Identifier("x"), "*", Identifier("y")),
            )
        ],
    )

    # if x + 2 * 2 then True
    assert parse(
        [
            Token("if", "identifier"),
            Token("x", "identifier"),
            Token("+", "operator"),
            Token("2", "integer"),
            Token("*", "operator"),
            Token("2", "integer"),
            Token("then", "identifier"),
            Token("True", "identifier"),
        ]
    ) == Module(
        [],
        [
            IfThenElse(
                BinaryOp(Identifier("x"), "+", BinaryOp(Literal(2), "*", Literal(2))),
                Identifier("True"),
                None,
            )
        ],
    )

    # 5 * if x then if y then 2 else 3
    assert parse(
        [
            Token("5", "integer"),
            Token("*", "operator"),
            Token("if", "identifier"),
            Token("x", "identifier"),
            Token("then", "identifier"),
            Token("if", "identifier"),
            Token("y", "identifier"),
            Token("then", "identifier"),
            Token("2", "integer"),
            Token("else", "identifier"),
            Token("3", "integer"),
        ]
    ) == Module(
        [],
        [
            BinaryOp(
                Literal(5),
                "*",
                IfThenElse(
                    Identifier("x"),
                    IfThenElse(Identifier("y"), Literal(2), Literal(3)),
                    None,
                ),
            )
        ],
    )


def test_parser_functions() -> None:
    assert parse(tokenize("f(x, y + z)")) == Module(
        [],
        [
            FunctionCall(
                "f", [Identifier("x"), BinaryOp(Identifier("y"), "+", Identifier("z"))]
            )
        ],
    )

    assert parse(tokenize("print_int(27)")) == Module(
        [], [FunctionCall("print_int", [Literal(27)])]
    )

    assert parse(tokenize("main()")) == Module([], [FunctionCall("main", [])])


def test_parser_assignment() -> None:
    assert parse(tokenize("x = 24")) == Module([], [Assignment("x", Literal(24))])

    assert parse(tokenize("a = b = c = (d + 2)")) == Module(
        [],
        [
            Assignment(
                "a",
                Assignment(
                    "b",
                    Assignment("c", BinaryOp(Identifier("d"), "+", Literal(2))),
                ),
            )
        ],
    )

    assert parse(tokenize("if True then x = y == 12 or 300 > z * 2")) == Module(
        [],
        [
            IfThenElse(
                Identifier("True"),
                Assignment(
                    "x",
                    BinaryOp(
                        BinaryOp(Identifier("y"), "==", Literal(12)),
                        "or",
                        BinaryOp(
                            Literal(300),
                            ">",
                            BinaryOp(Identifier("z"), "*", Literal(2)),
                        ),
                    ),
                ),
                None,
            )
        ],
    )

    assert parse(tokenize("2 * (hello = world)")) == Module(
        [], [BinaryOp(Literal(2), "*", Assignment("hello", Identifier("world")))]
    )


def test_parser_var() -> None:
    assert parse(tokenize("var a = b = c")) == Module(
        [],
        [
            VarDec(
                "a",
                Assignment("b", Identifier("c")),
            )
        ],
    )

    assert parse(tokenize("var x: Int = 2")) == Module(
        [], [VarDec("x", Literal(2), typ=Int)]
    )

    assert parse(tokenize("var x: () => Bool = always_true;")) == Module(
        [],
        [
            VarDec("x", Identifier("always_true"), typ=FunType([], Bool)),
        ],
    )

    assert parse(tokenize("var new_print: (Int) => Unit = print_int")) == Module(
        [], [VarDec("new_print", Identifier("print_int"), typ=FunType([Int], Unit))]
    )


def test_parser_block() -> None:
    assert parse(tokenize("{ x = y * 2 }")) == Module(
        [], [Block([Assignment("x", BinaryOp(Identifier("y"), "*", Literal(2)))])]
    )

    assert parse(tokenize("{ x = 2; 3 + 3 / 3; f(x); }")) == Module(
        [],
        [
            Block(
                [
                    Assignment("x", Literal(2)),
                    BinaryOp(Literal(3), "+", BinaryOp(Literal(3), "/", Literal(3))),
                    FunctionCall("f", [Identifier("x")]),
                    Literal(None),
                ]
            )
        ],
    )

    assert parse(tokenize("while True do { print_int(14); }")) == Module(
        [],
        [
            While(
                Identifier("True"),
                Block([FunctionCall("print_int", [Literal(14)]), Literal(None)]),
            )
        ],
    )

    assert (
        parse(
            tokenize(
                """
        {
            while f() do {
                var x = 10;
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
        == Module(
            [],
            [
                Block(
                    [
                        While(
                            FunctionCall("f", []),
                            Block(
                                [
                                    VarDec("x", Literal(10)),
                                    Assignment(
                                        "y",
                                        IfThenElse(
                                            FunctionCall("g", [Identifier("x")]),
                                            Block(
                                                [
                                                    Assignment(
                                                        "x",
                                                        BinaryOp(
                                                            Identifier("x"),
                                                            "+",
                                                            Literal(1),
                                                        ),
                                                    ),
                                                    Identifier("x"),
                                                ]
                                            ),
                                            Block(
                                                [FunctionCall("g", [Identifier("x")])]
                                            ),
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
            ],
        )
    )

    assert parse(tokenize("x = { { f(a) } { b } }")) == Module(
        [],
        [
            Assignment(
                "x",
                Block(
                    [
                        Block([FunctionCall("f", [Identifier("a")])]),
                        Block([Identifier("b")]),
                    ]
                ),
            )
        ],
    )

    assert (
        parse(tokenize("{ { x } { y } }"))
        == parse(tokenize("{ { x };{ y } }"))
        != parse(tokenize("{ { x };{ y };}"))
    )

    assert parse(tokenize("{ if true then { a } else { b } c }")) == parse(
        tokenize("{ if true then { a } else { b };c }")
    )

    assert parse(tokenize("x = 42; 14; print(x)")) == Module(
        [],
        [
            Assignment("x", Literal(42)),
            Literal(14),
            FunctionCall("print", [Identifier("x")]),
        ],
    )

    assert parse(tokenize("var x = { 42 } print(x)")) == Module(
        [],
        [
            VarDec("x", Block([Literal(42)])),
            FunctionCall("print", [Identifier("x")]),
        ],
    )

    assert parse(
        tokenize("while true do { var x = 2; if x == 2 then break else continue }")
    ) == Module(
        [],
        [
            While(
                Literal(True),
                Block(
                    [
                        VarDec("x", Literal(2)),
                        IfThenElse(
                            BinaryOp(Identifier("x"), "==", Literal(2)),
                            LoopControl("break"),
                            LoopControl("continue"),
                        ),
                    ]
                ),
            )
        ],
    )
