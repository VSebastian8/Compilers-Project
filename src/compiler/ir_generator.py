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
    root_expr: ast.Expression, reserved_names: set[str]
) -> list[ir.Instruction]:
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

    def visit(expr: ast.Expression, ir_table: ir.IRTab) -> ir.IRVar:
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
                var_exp = visit(expr.exp, ir_table)
                ins.append(ir.Call(var_op, [var_exp], var_result, loc=loc))
                return var_result

            case ast.BinaryOp():
                var_op = get_ir_var(expr.op, ir_table)
                short = var_op == ir.IRVar("or") or var_op == ir.IRVar("and")

                var_result = new_var()
                var_left = visit(expr.left, ir_table)

                end_label = new_label() if short else None
                if end_label is not None:
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

                var_right = visit(expr.right, ir_table)
                ins.append(ir.Call(var_op, [var_left, var_right], var_result, loc=loc))

                if end_label is not None:
                    ins.append(end_label)

                return var_result

            case ast.Assignment():
                var_left = get_ir_var(expr.left, ir_table)
                var_right = visit(expr.right, ir_table)
                ins.append(ir.Copy(var_left, var_right, loc=loc))
                return var_left

            case ast.VarDec():
                var_left = new_var()
                var_right = visit(expr.right, ir_table)
                ins.append(ir.Copy(var_left, var_right, loc=loc))
                ir_table.locals[expr.left] = var_left
                return var_left

            case ast.IfThenElse():
                if expr.otherwise is None:
                    l_then = new_label()
                    l_end = new_label()

                    var_cond = visit(expr.condition, ir_table)
                    ins.append(ir.CondJump(var_cond, l_then, l_end, loc=loc))

                    ins.append(l_then)
                    visit(expr.then, ir_table)
                    ins.append(l_end)

                    return var_unit
                else:
                    l_then = new_label()
                    l_else = new_label()
                    l_end = new_label()

                    var_res = new_var()
                    var_cond = visit(expr.condition, ir_table)
                    ins.append(ir.CondJump(var_cond, l_then, l_else, loc=loc))

                    ins.append(l_then)
                    var_then = visit(expr.then, ir_table)
                    ins.append(ir.Copy(var_then, var_res, loc=loc))
                    ins.append(ir.Jump(l_end, loc=loc))

                    ins.append(l_else)
                    var_else = visit(expr.otherwise, ir_table)
                    ins.append(ir.Copy(var_else, var_res, loc=loc))
                    ins.append(l_end)

                    return var_res

        return var_unit

    root_irtab = ir.IRTab({}, None)
    for name in reserved_names:
        root_irtab.locals[name] = ir.IRVar(name)

    var_final_result = visit(root_expr, root_irtab)

    if root_expr.typ == Int:
        ins.append(
            ir.Call(
                ir.IRVar("print_int"), [var_final_result], var_unit, loc=Location(0, 0)
            )
        )
    elif root_expr.typ == Bool:
        ins.append(
            ir.Call(
                ir.IRVar("print_bool"), [var_final_result], var_unit, loc=Location(0, 0)
            )
        )
    return ins
