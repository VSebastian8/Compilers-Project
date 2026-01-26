from compiler.tokenizer import tokenize
from compiler.parser import parse
from compiler.typechecker import typecheck
from compiler.ir_generator import generate_ir
from compiler.ir import reserved_names
from compiler.ast import Expression
from compiler.ir import LoadIntConst, Call, IRVar


def get_ast(program: str) -> Expression:
    program_ast = parse(tokenize(program))
    typecheck(program_ast)
    return program_ast


def test_ir_basics() -> None:
    assert generate_ir(get_ast("1 + 2 + 3"), reserved_names) == [
        LoadIntConst(1, IRVar("X_0")),
        LoadIntConst(2, IRVar("X_1")),
        Call(IRVar("+"), [IRVar("X_0"), IRVar("X_1")], IRVar("X_2")),
        LoadIntConst(3, IRVar("X_3")),
        Call(IRVar("+"), [IRVar("X_2"), IRVar("X_3")], IRVar("X_4")),
        Call(IRVar("print_int"), [IRVar("X_4")], IRVar("unit")),
    ]
