from compiler.tokenizer import tokenize
from compiler.token import Location
from compiler.parser import parse
from compiler.typechecker import typecheck
from compiler.types import Int, Bool, Unit
from compiler.ast import Block, Literal, While, Assignment, VarDec, Identifier, BinaryOp


def test_typechecker_basics() -> None:
    assert typecheck(parse(tokenize("2 + 3"))) == Int

    assert typecheck(parse(tokenize("2 < 3"))) == Bool

    assert typecheck(parse(tokenize("not (4 == 5)"))) == Bool

    assert typecheck(parse(tokenize("10 + 2 * 2 >= 5 or false"))) == Bool

    assert typecheck(parse(tokenize("var x: Int = 7"))) == Unit

    assert typecheck(parse(tokenize("var f: (Int) => Unit = print_int;"))) == Unit


def test_typechecker_blocks() -> None:
    assert typecheck(parse(tokenize("var x = 2 + 3; x"))) == Int

    assert typecheck(parse(tokenize("if true then true else false"))) == Bool

    assert typecheck(parse(tokenize("if true then print_int(24)"))) == Unit

    assert (
        typecheck(parse(tokenize("var x = 2; while x < 5  do { x = x + 1; }"))) == Unit
    )

    palindrome_program = parse(
        tokenize(
            """ # Check whether a number is a palindrome
            var y: Int = 202; /* input number */
            {
                var x = y; /* local copy */
                var reversed = 0;
                while x != 0 do {
                    reversed = reversed * 10 + x % 10;
                    # Modify local copy
                    x = x / 10;
                }
                reversed == y
            }
            """
        )
    )

    assert typecheck(palindrome_program) == Bool

    # Check that the type annotations in the ast are now correct (not Unit like before)
    assert palindrome_program == Block(
        [
            VarDec(
                "y",
                Literal(202, loc=Location(1, 25), typ=Int),
                loc=Location(1, 12),
                typ=Unit,
            ),
            Block(
                [
                    VarDec(
                        "x",
                        Identifier("y", loc=Location(3, 24), typ=Int),
                        loc=Location(3, 16),
                        typ=Unit,
                    ),
                    VarDec(
                        "reversed",
                        Literal(0, loc=Location(4, 31), typ=Int),
                        loc=Location(4, 16),
                        typ=Unit,
                    ),
                    While(
                        BinaryOp(
                            Identifier("x", loc=Location(5, 22), typ=Int),
                            "!=",
                            Literal(0, loc=Location(5, 27), typ=Int),
                            loc=Location(5, 22),
                            typ=Bool,
                        ),
                        Block(
                            [
                                Assignment(
                                    "reversed",
                                    BinaryOp(
                                        BinaryOp(
                                            Identifier(
                                                "reversed", loc=Location(6, 31), typ=Int
                                            ),
                                            "*",
                                            Literal(10, loc=Location(6, 42), typ=Int),
                                            loc=Location(6, 31),
                                            typ=Int,
                                        ),
                                        "+",
                                        BinaryOp(
                                            Identifier(
                                                "x", loc=Location(6, 47), typ=Int
                                            ),
                                            "%",
                                            Literal(10, loc=Location(6, 51), typ=Int),
                                            loc=Location(6, 47),
                                            typ=Int,
                                        ),
                                        loc=Location(6, 31),
                                        typ=Int,
                                    ),
                                    loc=Location(6, 20),
                                    typ=Int,
                                ),
                                Assignment(
                                    "x",
                                    BinaryOp(
                                        Identifier("x", loc=Location(8, 24), typ=Int),
                                        "/",
                                        Literal(10, loc=Location(8, 28), typ=Int),
                                        loc=Location(8, 24),
                                        typ=Int,
                                    ),
                                    loc=Location(8, 20),
                                    typ=Int,
                                ),
                                Literal(None, loc=Location(-1, -1), typ=Unit),
                            ],
                            loc=Location(5, 32),
                            typ=Unit,
                        ),
                        loc=Location(5, 16),
                        typ=Unit,
                    ),
                    BinaryOp(
                        Identifier("reversed", loc=Location(10, 16), typ=Int),
                        "==",
                        Identifier("y", loc=Location(10, 28), typ=Int),
                        loc=Location(10, 16),
                        typ=Bool,
                    ),
                ],
                loc=Location(2, 12),
                typ=Bool,
            ),
        ],
        loc=Location(0, 0),
        typ=Bool,
    )


def test_typechecker_errors() -> None:
    import pytest, re

    with pytest.raises(
        Exception,
        match=re.escape(
            "(0, 0): [Type error] cannot apply operator not to value of type Int"
        ),
    ):
        typecheck(parse(tokenize("not(1 + 1)")))

    with pytest.raises(
        Exception,
        match=re.escape(
            "(0, 0): [Type error] operator < expected types (Int, Int) but found (Int, Bool)"
        ),
    ):
        typecheck(parse(tokenize("2 < true")))

    with pytest.raises(
        Exception,
        match=re.escape(
            "(0, 15): [Type error] function print_int has type (Int) => Unit but it's been called with the following types [Bool]"
        ),
    ):
        typecheck(parse(tokenize("var x = false; print_int(x)")))

    with pytest.raises(
        Exception,
        match=re.escape(
            '(2, 20): while block must return the Unit type, add ";" after last statement'
        ),
    ):
        typecheck(
            parse(
                tokenize(
                    """
                    var index = 0; 
                    while index < 10 do { index = index + 1 }         
                    """
                )
            )
        )

    with pytest.raises(
        Exception,
        match=re.escape(
            "(0, 12): [Type error] cannot assign value of type Bool to variable x of type Int"
        ),
    ):
        typecheck(parse(tokenize(" var x = 7; x = true;")))

    with pytest.raises(
        Exception,
        match=re.escape(
            "(0, 0): [Type error] assigned type Int conflicts with declared type Bool"
        ),
    ):
        typecheck(parse(tokenize("var index: Bool = 0;")))
