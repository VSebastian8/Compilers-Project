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
    assert (
        generate_ir(
            get_ast(
                """
                var n: Int = 11;
                var i = 2; var done = false;
                while i <= n and done == false do {
                    print_int(i);
                    var i = n % i;
                    if i == 0 then {
                        done = true;
                    }
                }
                """
            ),
            reserved_names,
        )
        == [
            LoadIntConst(value=11, dest=IRVar("X_2")),
            Copy(source=IRVar("X_2"), dest=IRVar("X_1")),
            LoadIntConst(value=2, dest=IRVar("X_4")),
            Copy(source=IRVar("X_4"), dest=IRVar("X_3")),
            LoadBoolConst(value=False, dest=IRVar("X_6")),
            Copy(source=IRVar("X_6"), dest=IRVar("X_5")),
            Label("L_0"),
            Call(fun=IRVar("<="), args=[IRVar("X_3"), IRVar("X_1")], dest=IRVar("X_8")),
            CondJump(IRVar("X_8"), Label("L_5"), Label("L_4")),
            Label("L_4"),
            Copy(source=IRVar("X_8"), dest=IRVar("X_7")),
            Jump(Label("L_3")),
            Label("L_5"),
            LoadBoolConst(value=False, dest=IRVar("X_10")),
            Call(
                fun=IRVar("=="), args=[IRVar("X_5"), IRVar("X_10")], dest=IRVar("X_9")
            ),
            Call(
                fun=IRVar("and"), args=[IRVar("X_8"), IRVar("X_9")], dest=IRVar("X_7")
            ),
            Label("L_3"),
            CondJump(IRVar("X_7"), Label("L_1"), Label("L_2")),
            Label("L_1"),
            Call(fun=IRVar("print_int"), args=[IRVar("X_3")], dest=IRVar("X_12")),
            Call(fun=IRVar("%"), args=[IRVar("X_1"), IRVar("X_3")], dest=IRVar("X_14")),
            Copy(source=IRVar("X_14"), dest=IRVar("X_13")),
            LoadIntConst(value=0, dest=IRVar("X_16")),
            Call(
                fun=IRVar("=="), args=[IRVar("X_13"), IRVar("X_16")], dest=IRVar("X_15")
            ),
            CondJump(IRVar("X_15"), Label("L_6"), Label("L_7")),
            Label("L_6"),
            LoadBoolConst(value=True, dest=IRVar("X_18")),
            Copy(source=IRVar("X_18"), dest=IRVar("X_5")),
            Copy(source=IRVar("unit"), dest=IRVar("X_17")),
            Label("L_7"),
            Copy(source=IRVar("unit"), dest=IRVar("X_11")),
            Jump(Label("L_0")),
            Label("L_2"),
            Copy(source=IRVar("unit"), dest=IRVar("X_0")),
        ]
    )
