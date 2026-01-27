from compiler.tokenizer import tokenize
from compiler.parser import parse
from compiler.typechecker import typecheck
from compiler.ir_generator import generate_ir
from compiler.ir import reserved_names
from compiler.ast import Expression
from compiler.ir import (
    LoadIntConst,
    Call,
    IRVar,
    CondJump,
    Label,
    Jump,
    Copy,
    LoadBoolConst,
)


def get_ast(program: str) -> Expression:
    program_ast = parse(tokenize(program))
    typecheck(program_ast)
    return program_ast


def test_ir_basics() -> None:
    assert generate_ir(get_ast("1 + 2 + 3"), reserved_names) == [
        LoadIntConst(1, IRVar("X_2")),
        LoadIntConst(2, IRVar("X_3")),
        Call(IRVar("+"), [IRVar("X_2"), IRVar("X_3")], IRVar("X_1")),
        LoadIntConst(3, IRVar("X_4")),
        Call(IRVar("+"), [IRVar("X_1"), IRVar("X_4")], IRVar("X_0")),
        Call(IRVar("print_int"), [IRVar("X_0")], IRVar("unit")),
    ]

    assert generate_ir(get_ast("100 + 5 * 25"), reserved_names) == [
        LoadIntConst(100, IRVar("X_1")),
        LoadIntConst(5, IRVar("X_3")),
        LoadIntConst(25, IRVar("X_4")),
        Call(IRVar("*"), [IRVar("X_3"), IRVar("X_4")], IRVar("X_2")),
        Call(IRVar("+"), [IRVar("X_1"), IRVar("X_2")], IRVar("X_0")),
        Call(IRVar("print_int"), [IRVar("X_0")], IRVar("unit")),
    ]

    assert generate_ir(get_ast("if 10 < 12 then 1 else 0"), reserved_names) == [
        LoadIntConst(10, IRVar("X_2")),
        LoadIntConst(12, IRVar("X_3")),
        Call(IRVar("<"), [IRVar("X_2"), IRVar("X_3")], IRVar("X_1")),
        CondJump(IRVar("X_1"), Label("L_0"), Label("L_1")),
        Label("L_0"),
        LoadIntConst(1, IRVar("X_4")),
        Copy(IRVar("X_4"), IRVar("X_0")),
        Jump(Label("L_2")),
        Label("L_1"),
        LoadIntConst(0, IRVar("X_5")),
        Copy(IRVar("X_5"), IRVar("X_0")),
        Label("L_2"),
        Call(IRVar("print_int"), [IRVar("X_0")], IRVar("unit")),
    ]

    # Short-circuit test
    assert generate_ir(get_ast("true and false"), reserved_names) == [
        LoadBoolConst(True, IRVar("X_1")),
        CondJump(IRVar("X_1"), Label("L_2"), Label("L_1")),
        Label("L_1"),
        Copy(IRVar("X_1"), IRVar("X_0")),
        Jump(Label("L_0")),
        Label("L_2"),
        LoadBoolConst(False, IRVar("X_2")),
        Call(IRVar("and"), [IRVar("X_1"), IRVar("X_2")], IRVar("X_0")),
        Label("L_0"),
        Call(IRVar("print_bool"), [IRVar("X_0")], IRVar("unit")),
    ]


def test_ir_blocks() -> None:
    assert True
