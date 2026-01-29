from compiler import ast, ir
from compiler.types import Bool, Int, Unit
from compiler.token import Location


def get_ir_var(var: str, ir_table: ir.IRTab) -> ir.IRVar:
    if var in ir_table.locals:
        return ir_table.locals[var]
    else:
        match ir_table.parent:
            case None:
                raise Exception(f"{var} not defined")
            case ir_tab:
                return get_ir_var(var, ir_tab)


def generate_ir(
    mod: ast.Module, reserved_names: set[str]
) -> dict[str, list[ir.Instruction]]:
    """Returns the instructions for each function"""
    var_unit = ir.IRVar("unit")

    current_var = -1
    current_label = -1

    def new_var() -> ir.IRVar:
        nonlocal current_var
        current_var += 1
        return ir.IRVar(f"X_{current_var}")

    def new_label() -> ir.Label:
        nonlocal current_label
        current_label += 1
        return ir.Label(f"L_{current_label}")

    ins: list[ir.Instruction] = []

    def visit(
        expr: ast.Expression,
        ir_table: ir.IRTab,
        while_start: None | ir.Label = None,
        while_end: None | ir.Label = None,
    ) -> ir.IRVar:
        loc = expr.loc

        match expr:
            case ast.Literal():
                match expr.value:
                    case bool():
                        var = new_var()
                        ins.append(ir.LoadBoolConst(expr.value, var, loc=loc))
                    case int():
                        var = new_var()
                        ins.append(ir.LoadIntConst(expr.value, var, loc=loc))
                    case None:
                        var = var_unit
                    case _:
                        raise Exception(
                            f"{loc}: unsupported literal: {type(expr.value)}"
                        )
                return var

            case ast.Identifier():
                return get_ir_var(expr.name, ir_table)

            case ast.UnaryOp():
                var_op = get_ir_var(f"unary_{expr.op}", ir_table)
                var_result = new_var()
                var_exp = visit(expr.exp, ir_table, while_start, while_end)
                ins.append(ir.Call(var_op, [var_exp], var_result, loc=loc))
                return var_result

            case ast.BinaryOp():
                var_op = get_ir_var(expr.op, ir_table)
                var_result = new_var()
                var_left = visit(expr.left, ir_table, while_start, while_end)

                if var_op == ir.IRVar("or") or var_op == ir.IRVar("and"):
                    end_label = new_label()

                    short_label = new_label()
                    long_label = new_label()
                    if var_op == ir.IRVar("or"):
                        ins.append(
                            ir.CondJump(var_left, short_label, long_label, loc=loc)
                        )
                    elif var_op == ir.IRVar("and"):
                        ins.append(
                            ir.CondJump(var_left, long_label, short_label, loc=loc)
                        )
                    ins.append(short_label)
                    ins.append(ir.Copy(var_left, var_result, loc=loc))
                    ins.append(ir.Jump(end_label, loc=loc))

                    ins.append(long_label)
                    var_right = visit(expr.right, ir_table, while_start, while_end)
                    ins.append(ir.Copy(var_right, var_result, loc=loc))
                    ins.append(end_label)
                else:
                    var_right = visit(expr.right, ir_table, while_start, while_end)
                    ins.append(
                        ir.Call(var_op, [var_left, var_right], var_result, loc=loc)
                    )

                return var_result

            case ast.Assignment():
                var_left = get_ir_var(expr.left, ir_table)
                var_right = visit(expr.right, ir_table, while_start, while_end)
                ins.append(ir.Copy(var_right, var_left, loc=loc))
                return var_left

            case ast.VarDec():
                var_left = new_var()
                var_right = visit(expr.right, ir_table, while_start, while_end)
                ins.append(ir.Copy(var_right, var_left, loc=loc))
                ir_table.locals[expr.left] = var_left
                return var_unit

            case ast.IfThenElse():
                if expr.otherwise is None:
                    l_then = new_label()
                    l_end = new_label()

                    var_cond = visit(expr.condition, ir_table)
                    ins.append(ir.CondJump(var_cond, l_then, l_end, loc=loc))

                    ins.append(l_then)
                    visit(expr.then, ir_table, while_start, while_end)
                    ins.append(l_end)

                    return var_unit
                else:
                    l_then = new_label()
                    l_else = new_label()
                    l_end = new_label()

                    var_result = new_var()
                    var_cond = visit(expr.condition, ir_table)
                    ins.append(ir.CondJump(var_cond, l_then, l_else, loc=loc))

                    ins.append(l_then)
                    var_then = visit(expr.then, ir_table, while_start, while_end)
                    ins.append(ir.Copy(var_then, var_result, loc=loc))
                    ins.append(ir.Jump(l_end, loc=loc))

                    ins.append(l_else)
                    var_else = visit(expr.otherwise, ir_table, while_start, while_end)
                    ins.append(ir.Copy(var_else, var_result, loc=loc))
                    ins.append(l_end)

                    return var_result

            case ast.FunctionCall():
                var_f = get_ir_var(expr.name, ir_table)
                var_result = new_var()
                args = [visit(arg, ir_table) for arg in expr.args]
                ins.append(ir.Call(var_f, args, var_result, loc=loc))
                return var_result

            case ast.Block():
                var_result = new_var()
                new_scope = ir.IRTab({}, ir_table)
                exps = [
                    visit(exp, new_scope, while_start, while_end)
                    for exp in expr.expressions
                ]
                ins.append(ir.Copy(exps[-1], var_result, loc=loc))
                return var_result

            case ast.While():
                l_cond = new_label()
                l_block = new_label()
                l_end = new_label()
                ins.append(l_cond)
                var_cond = visit(expr.condition, ir_table)
                ins.append(ir.CondJump(var_cond, l_block, l_end, loc=loc))
                ins.append(l_block)
                visit(expr.block, ir_table, while_start=l_cond, while_end=l_end)
                ins.append(ir.Jump(l_cond, loc=loc))
                ins.append(l_end)
                return var_unit

            case ast.LoopControl():
                if while_start is None or while_end is None:
                    raise Exception(
                        f"{expr.loc}: cannot have {expr.name} outside of while loop"
                    )
                if expr.name == "break":
                    ins.append(ir.Jump(while_end, loc=loc))
                else:
                    ins.append(ir.Jump(while_start, loc=loc))
                return var_unit

            case ast.Return():
                var_res = visit(expr.value, ir_table)
                ins.append(ir.Copy(var_res, ir.IRVar("%rax"), loc=loc))
                ins.append(ir.Jump(exit_label, loc=loc))

        return var_unit

    root_irtab = ir.IRTab({}, None)
    for name in reserved_names:
        root_irtab.locals[name] = ir.IRVar(name)
    for fun in mod.funs:
        root_irtab.locals[fun.name] = ir.IRVar(fun.name)

    fun_insn: dict[str, list[ir.Instruction]] = {}

    registers = ["%rdi", "%rsi", "%rdx", "%rcx", "%r8", "%r9"]
    for fun in mod.funs:
        ins = []
        new_table = ir.IRTab({}, root_irtab)
        for arg, reg in zip(fun.args, registers):
            arg_var = new_var()
            new_table.locals[arg.name] = arg_var
            ins.append(ir.Copy(ir.IRVar(reg), arg_var, loc=fun.loc))
        exit_label = new_label()
        visit(fun.body, new_table)
        ins.append(exit_label)
        fun_insn[fun.name] = ins.copy()

    ins = []
    var_final_result = var_unit
    new_table = ir.IRTab({}, root_irtab)
    for exp in mod.exps:
        var_final_result = visit(exp, new_table)
    if len(mod.exps) != 0:
        if mod.exps[-1].typ == Int:
            ins.append(
                ir.Call(
                    ir.IRVar("print_int"),
                    [var_final_result],
                    var_unit,
                    loc=Location(0, 0),
                )
            )
        elif mod.exps[-1].typ == Bool:
            ins.append(
                ir.Call(
                    ir.IRVar("print_bool"),
                    [var_final_result],
                    var_unit,
                    loc=Location(0, 0),
                )
            )
    fun_insn["main"] = ins.copy()
    return fun_insn
