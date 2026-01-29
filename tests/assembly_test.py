from compiler.tokenizer import tokenize
from compiler.parser import parse
from compiler.typechecker import typecheck
from compiler.ir_generator import generate_ir
from compiler.assembly_generator import generate_assembly
from compiler.ir import reserved_names


def test_assembly_gen() -> None:
    program = parse(tokenize("{ var x = true; if x then 1 else 2; }"))
    typecheck(program)
    assert (
        generate_assembly(
            generate_ir(
                program,
                reserved_names,
            ),
        )
        == """.extern print_int
.extern print_bool
.extern read_int
.global main
.type main, @function
.section .text

main:
pushq %rbp
movq %rsp, %rbp
subq $48, %rsp

# LoadBoolConst((0, 10), True, X_2)
movq $1, -8(%rbp)

# Copy((0, 2), X_2, X_1)
movq -8(%rbp), %rax
movq %rax, -16(%rbp)

# CondJump((0, 16), X_1, Label((-1, -1), L_0), Label((-1, -1), L_1))
cmpq $0, -16(%rbp)
jne .LL_0
jmp .LL_1

# Label((-1, -1), L_0)
.LL_0:

# LoadIntConst((0, 26), 1, X_4)
movq $1, -24(%rbp)

# Copy((0, 16), X_4, X_3)
movq -24(%rbp), %rax
movq %rax, -32(%rbp)

# Jump((0, 16), Label((-1, -1), L_2))
jmp .LL_2

# Label((-1, -1), L_1)
.LL_1:

# LoadIntConst((0, 33), 2, X_5)
movq $2, -40(%rbp)

# Copy((0, 16), X_5, X_3)
movq -40(%rbp), %rax
movq %rax, -32(%rbp)

# Label((-1, -1), L_2)
.LL_2:

# Copy((0, 0), unit, X_0)

movq $0, %rax
movq %rbp, %rsp
popq %rbp
ret
"""
    )
