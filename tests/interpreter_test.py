from compiler.tokenizer import tokenize
from compiler.parser import parse
from compiler.interpreter import interpret
from unittest.mock import patch, call
from typing import Any


def test_interpreter_basics() -> None:
    assert interpret(parse(tokenize("1 + 2"))) == 3

    assert interpret(parse(tokenize("4 / 2"))) == 2

    assert interpret(parse(tokenize("50 * 10"))) == 500

    assert interpret(parse(tokenize("(5 + 4) % 2"))) == 1

    assert interpret(parse(tokenize("-3 + 2"))) == -1

    assert interpret(parse(tokenize("2 < 3 and 2 == 1 + 1"))) == True


def test_interpreter_blocks() -> None:
    assert interpret(parse(tokenize("1 + 2; 2 + 3"))) == 5

    assert interpret(parse(tokenize("var x = 2; x + 3"))) == 5

    assert interpret(parse(tokenize("var x = 2; x = x + 3; x"))) == 5

    assert (
        interpret(
            parse(tokenize("var x = 17; if x == 24 then 12 else { var y = x; x + 1}"))
        )
        == 18
    )


@patch("builtins.print")
def test_interpreter_function(printed_output: Any) -> None:
    assert interpret(parse(tokenize("print_int(27)"))) == None

    assert interpret(parse(tokenize("var x = 12; print_int(x + 5)"))) == None

    assert printed_output.mock_calls == [call(27), call(17)]

    assert (
        interpret(parse(tokenize("var x = 3; if (x % 2 == 1) then print_int(x == 3)")))
        == None
    )

    assert printed_output.mock_calls == [call(27), call(17), call(True)]


@patch("builtins.print")
def test_interpreter_while(printed_output: Any) -> None:
    assert interpret(parse(tokenize("var i = 0; while i < 5 do { i = i + 1; i}"))) == 5

    def prim_program(n: int) -> str:
        return (
            f"""
            var n = {n}; 
            """
            + """
            if (n % 2 == 0)
                then print_int(0)
                else {
                    var i = 3;
                    var prime = true;
                    while i < n do { 
                        if n % i == 0 then prime = false;
                        i = i + 2;
                    }
                    if prime
                        then print_int(1)
                        else print_int(0)
                }
            """
        )

    assert interpret(parse(tokenize(prim_program(27)))) == None
    assert interpret(parse(tokenize(prim_program(28)))) == None
    assert interpret(parse(tokenize(prim_program(29)))) == None
    assert printed_output.mock_calls == [call(0), call(0), call(1)]
