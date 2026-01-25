from compiler.tokenizer import tokenize
from compiler.parser import parse
from compiler.typechecker import typecheck
from compiler.types import Int, Bool, Unit


def test_typechecker_basics() -> None:
    assert typecheck(parse(tokenize("2 + 3"))) == Int

    assert typecheck(parse(tokenize("var x = 2 + 3; x"))) == Int

    assert typecheck(parse(tokenize("if true then true else false"))) == Bool

    assert (
        typecheck(parse(tokenize("var x = 2; while x < 5  do { x = x + 1; }"))) == Unit
    )
