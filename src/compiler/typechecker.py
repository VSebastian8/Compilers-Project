import compiler.types as types
import compiler.ast as ast


def get_var_type(var: str, type_table: types.TypeTab) -> types.Type:
    if var in type_table.locals:
        return type_table.locals[var]
    else:
        match type_table.parent:
            case None:
                raise Exception(f"{var} not defined")
            case type_tab:
                return get_var_type(var, type_tab)


def set_var_type(var: str, typ: types.Type, type_table: types.TypeTab) -> None:
    if var in type_table.locals:
        type_table.locals[var] = typ
    else:
        match type_table.parent:
            case None:
                raise Exception(f"{var} not defined")
            case type_tab:
                set_var_type(var, typ, type_tab)


def typecheck(
    node: ast.Expression | ast.Module,
    type_table: types.TypeTab = types.top_level,
    fun_type: types.Type | None = None,
) -> types.Type:
    typ = get_type(node, type_table, fun_type)
    if not isinstance(node, ast.Module):
        node.typ = typ
    return typ


def get_type(
    node: ast.Expression | ast.Module,
    type_table: types.TypeTab = types.top_level,
    fun_type: types.Type | None = None,
) -> types.Type:
    match node:
        case ast.Literal():
            if node.value == None:
                return types.Unit
            if isinstance(node.value, bool):
                return types.Bool
            return types.Int

        case ast.Identifier():
            return get_var_type(node.name, type_table)

        case ast.VarDec():
            name: str = node.left
            if name in type_table.locals:
                raise Exception(
                    f"{node.loc}: cannot declare variable {name} multiple times"
                )
            typ: types.Type = typecheck(node.right, type_table, fun_type)
            if node.typ != types.Unit and node.typ != typ:
                raise Exception(
                    f"{node.loc}: [Type error] assigned type {typ} conflicts with declared type {node.typ}"
                )
            type_table.locals[name] = typ
            return types.Unit

        case ast.Assignment():
            name = node.left
            left_typ = get_var_type(name, type_table)
            right_typ = typecheck(node.right, type_table, fun_type)
            if left_typ is not right_typ:
                raise Exception(
                    f"{node.loc}: [Type error] cannot assign value of type {right_typ} to variable {name} of type {left_typ}"
                )
            return right_typ

        case ast.UnaryOp():
            typ = typecheck(node.exp, type_table, fun_type)
            op = get_var_type(f"unary_{node.op}", type_table)
            if isinstance(op, types.FunType):
                if op.args[0] != typ:
                    raise Exception(
                        f"{node.loc}: [Type error] cannot apply operator {node.op} to value of type {typ}"
                    )
                return op.ret
            raise Exception(f"{node.loc}: {node.op} is not an operator")

        case ast.BinaryOp():
            t1 = typecheck(node.left, type_table, fun_type)
            t2 = typecheck(node.right, type_table, fun_type)
            if node.op == "==" or node.op == "!=":
                if t1 != t2:
                    raise Exception(
                        f"{node.op}: [Type error] cannot compare types {t1} and {t2}"
                    )
                return types.Bool
            op = get_var_type(node.op, type_table)
            if isinstance(op, types.FunType):
                if op.args[0] != t1 or op.args[1] != t2:
                    raise Exception(
                        f"{node.loc}: [Type error] operator {node.op} expected types ({op.args[0]}, {op.args[1]}) but found ({t1}, {t2})"
                    )
                return op.ret
            raise Exception(f"{node.loc}: {node.op} is not an operator")

        case ast.IfThenElse():
            t1 = typecheck(node.condition, type_table, fun_type)
            if t1 is not types.Bool:
                raise Exception(
                    f"{node.loc}: [Type error] if condition must be of type Bool not {t1}"
                )
            t2 = typecheck(node.then, type_table, fun_type)
            if node.otherwise is None and isinstance(node.then, ast.Block):
                return types.Unit
            t3 = (
                types.Unit
                if node.otherwise is None
                else typecheck(node.otherwise, type_table, fun_type)
            )
            if t2 is not t3:
                raise Exception(
                    f"{node.loc}: [Type error] if branches must have the same type, not {t2} and {t3}"
                )
            return t2

        case ast.While():
            t1 = typecheck(node.condition, type_table, fun_type)
            if t1 is not types.Bool:
                raise Exception(
                    f"{node.loc}: [Type error] while condition must be of type Bool not {t1}"
                )
            typ = typecheck(node.block, type_table, fun_type)
            if typ is not types.Unit:
                raise Exception(
                    f'{node.loc}: while block must return the Unit type, add ";" after last statement'
                )
            return types.Unit

        case ast.FunctionCall():
            func = get_var_type(node.name, type_table)
            if isinstance(func, types.FunType):
                call_types = []
                for arg in node.args:
                    call_types.append(typecheck(arg, type_table, fun_type))
                if func.args != call_types:
                    raise Exception(
                        f"{node.loc}: [Type error] function {node.name} has type {func.name} but it's been called with the following types {call_types}"
                    )
                return func.ret
            raise Exception(f"{node.loc}: {node.name} is not a function")

        case ast.Block():
            new_scope = types.TypeTab({}, type_table)
            print(f"In block scope {new_scope}")
            return_val = types.Unit
            for exp in node.expressions:
                return_val = typecheck(exp, new_scope, fun_type)
            return return_val

        case ast.LoopControl():
            return types.Unit

        case ast.FunDef():
            new_scope = types.TypeTab({}, type_table)
            for arg in node.args:
                new_scope.locals[arg.name] = arg.typ
            print(f"In fun {node.name} locals {new_scope.locals}")
            typecheck(node.body, new_scope, node.typ)
            return node.typ

        case ast.Return():
            typ = typecheck(node.value, type_table)
            if fun_type == None:
                raise Exception(
                    f"{node.loc}: cannot call return outside of function definition"
                )
            if isinstance(fun_type, types.FunType):
                if typ != fun_type.ret:
                    raise Exception(
                        f"{node.loc}: return type {typ} doesn't match function type {fun_type}"
                    )
            return typ

        case ast.Module():
            return_val = types.Unit
            top_scope = types.TypeTab({}, type_table)
            for fun in node.funs:
                top_scope.locals[fun.name] = fun.typ
            for fun in node.funs:
                typecheck(fun, top_scope, None)
            for exp in node.exps:
                return_val = typecheck(exp, top_scope, None)
            return return_val

    return types.Unit
