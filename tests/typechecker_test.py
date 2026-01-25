from compiler.tokenizer import tokenize
from compiler.parser import parse
from compiler.typechecker import typecheck
from compiler.types import Int, Bool, Unit


def test_typechecker_basics() -> None:
    assert typecheck(parse(tokenize("2 + 3"))) == Int

    assert typecheck(parse(tokenize("2 < 3"))) == Bool

    assert typecheck(parse(tokenize("not (4 == 5)"))) == Bool

    assert typecheck(parse(tokenize("10 + 2 * 2 >= 5 or false"))) == Bool


def test_typechecker_blocks() -> None:
    assert typecheck(parse(tokenize("var x = 2 + 3; x"))) == Int

    assert typecheck(parse(tokenize("if true then true else false"))) == Bool

    assert typecheck(parse(tokenize("if true then print_int(24)"))) == Unit

    assert (
        typecheck(parse(tokenize("var x = 2; while x < 5  do { x = x + 1; }"))) == Unit
    )

    assert (
        typecheck(
            parse(
                tokenize(
                    """
                    var y = 202; 
                    {
                        var x = y;
                        var reversed = 0;
                        while x != 0 do {
                            reversed = reversed * 10 + x % 10;
                            x = x / 10;
                        }
                        reversed == y
                    }
                    """
                )
            )
        )
        == Bool
    )


def test_typechecker_errors() -> None:
    import pytest, re

    with pytest.raises(
        Exception,
        match=re.escape(
            "(0, 0): Type error: operator < expected types (Int, Int) but found (Int, Bool)"
        ),
    ):
        typecheck(parse(tokenize("2 < true")))

    with pytest.raises(
        Exception,
        match=re.escape(
            "(0, 15) Type error: Function print_int has type Int -> Unit but it's been called with the following types [Bool]"
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
