from compiler import ir
from dataclasses import fields


class Locals:
    """Knows the memory location of every local variable."""

    _var_to_location: dict[ir.IRVar, str]
    _stack_used: int

    def __init__(self, variables: list[ir.IRVar]) -> None:
        self._var_to_location = {}
        current = 0
        for var in variables:
            if var not in self._var_to_location:
                current -= 8
                self._var_to_location[var] = f"{current}(%rbp)"
        self._stack_used = -current

    def get_ref(self, v: ir.IRVar) -> str:
        """Returns an Assembly reference like `-24(%rbp)`
        for the memory location that stores the given variable"""
        return self._var_to_location[v]

    def stack_used(self) -> int:
        """Returns the number of bytes of stack space needed for the local variables."""
        return self._stack_used


def get_all_ir_variables(instructions: list[ir.Instruction]) -> list[ir.IRVar]:
    result_list: list[ir.IRVar] = []
    result_set: set[ir.IRVar] = set()

    def add(v: ir.IRVar) -> None:
        if v not in result_set:
            result_list.append(v)
            result_set.add(v)

    for insn in instructions:
        for field in fields(insn):
            value = getattr(insn, field.name)
            if isinstance(value, ir.IRVar):
                add(value)
            elif isinstance(value, list):
                for v in value:
                    if isinstance(v, ir.IRVar):
                        add(v)
    return result_list


def generate_assembly(instructions: list[ir.Instruction]) -> str:
    lines = []

    def emit(line: str) -> None:
        lines.append(line)

    locals = Locals(variables=get_all_ir_variables(instructions))

    initial_decl = [
        ".extern print_int",
        ".extern print_bool",
        ".extern read_int",
        ".global main",
        ".type main, @function",
        ".section .text",
        "",
        "main:",
        "pushq %rbp",
        "movq %rsp, %rbp",
        f"subq ${locals._stack_used}, %rsp",
    ]
    for decl in initial_decl:
        emit(decl)

    for insn in instructions:
        emit("")
        emit("# " + str(insn))
        match insn:
            case ir.Label():
                # ".L" prefix marks the symbol as "private"
                emit(f".L{insn.name}:")
            case ir.LoadIntConst():
                if -(2**31) <= insn.value < 2**31:
                    emit(f"movq ${insn.value}, {locals.get_ref(insn.dest)}")
                else:
                    # Larger integers
                    emit(f"movabsq ${insn.value}, %rax")
                    emit(f"movq %rax, {locals.get_ref(insn.dest)}")
            case ir.LoadBoolConst():
                emit(f"movq ${1 if insn.value else 0}, {locals.get_ref(insn.dest)}")
            case ir.Jump():
                emit(f"jmp .L{insn.label.name}")
            case ir.Copy():
                emit(f"movq {locals.get_ref(insn.source)}, %rax")
                emit(f"movq %rax, {locals.get_ref(insn.dest)}")
            case ir.CondJump():
                emit(f"cmpq $0, {locals.get_ref(insn.cond)}")
                emit(f"jne .L{insn.then_label}")
                emit(f"jmp .L{insn.else_label}")
    emit("movq $0, %rax")
    emit("movq %rbp, %rsp")
    emit("popq %rbp")
    emit("ret")
    return "\n".join(lines)
