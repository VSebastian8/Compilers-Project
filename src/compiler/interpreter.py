from typing import Any, Self
from compiler import ast
from dataclasses import dataclass
from collections.abc import Callable

type Value = int | bool | Callable | None


@dataclass
class SymTab:
    locals: dict[str, Value]
    parent: Self | None


def print_int(x: int) -> None:
    print(x)
    return None


def print_bool(x: bool) -> None:
    print(x)
    return None


top_level: SymTab = SymTab(
    {
        "true": True,
        "false": False,
        "unit": None,
        "+": (lambda x, y: x + y),
        "-": (lambda x, y: x - y),
        "*": (lambda x, y: x * y),
        "/": (lambda x, y: x / y),
        "%": (lambda x, y: x % y),
        "<": (lambda x, y: x < y),
        "<=": (lambda x, y: x <= y),
        ">": (lambda x, y: x > y),
        ">=": (lambda x, y: x >= y),
        "==": (lambda x, y: x == y),
        "!=": (lambda x, y: x != y),
        "or": (lambda x, y: x or y),
        "and": (lambda x, y: x and y),
        "unary_-": (lambda x: -x),
        "unary_not": (lambda x: not x),
        "print_int": print_int,
        "print_bool": print_bool,
    },
    None,
)


def find_variable(variable: str, symbol_table: SymTab) -> Value:
    if variable in symbol_table.locals:
        return symbol_table.locals[variable]
    else:
        match symbol_table.parent:
            case None:
                raise Exception(f"{variable} not defined")
            case sym_tab:
                return find_variable(variable, sym_tab)


def set_variable(variable: str, val: Value, symbol_table: SymTab) -> None:
    if variable in symbol_table.locals:
        symbol_table.locals[variable] = val
    else:
        match symbol_table.parent:
            case None:
                raise Exception(f"{variable} not defined")
            case sym_tab:
                set_variable(variable, val, sym_tab)


def interpret(node: ast.Expression, symbol_table: SymTab = top_level) -> Value:
    match node:
        case ast.Literal():
            return node.value

        case ast.Identifier():
            x: Any = node.name
            return find_variable(x, symbol_table)

        case ast.VarDec():
            name: str = node.left
            val: Value = interpret(node.right, symbol_table)
            if name in symbol_table.locals:
                raise Exception(f"Cannot declare variable {name} multiple times")
            symbol_table.locals[name] = val
            return val

        case ast.Assignment():
            name = node.left
            find_variable(name, symbol_table)
            val = interpret(node.right, symbol_table)
            set_variable(name, val, symbol_table)
            return val

        case ast.UnaryOp():
            exp: Any = interpret(node.exp, symbol_table)
            op: Value = find_variable(f"unary_{node.op}", symbol_table)
            if callable(op):
                return op(exp)
            raise Exception(f"{node.op} is not an operator")

        case ast.BinaryOp():
            a: Any = interpret(node.left, symbol_table)
            # Shortcircuit or & and
            if node.op == "or":
                if a == True:
                    return True
            elif node.op == "and":
                if a == False:
                    return False
            b: Any = interpret(node.right, symbol_table)
            opp: Value = find_variable(node.op, symbol_table)
            if callable(opp):
                return opp(a, b)
            raise Exception(f"{node.op} is not an operator")

        case ast.IfThenElse():
            if interpret(node.condition, symbol_table):
                return interpret(node.then, symbol_table)
            else:
                match node.otherwise:
                    case None:
                        return None
                    case e:
                        return interpret(e, symbol_table)

        case ast.While():
            return_val = None
            while interpret(node.condition, symbol_table):
                return_val = interpret(node.block, symbol_table)
            return return_val

        case ast.FunctionCall():
            func = find_variable(node.name, symbol_table)
            arg_list = []
            for arg in node.args:
                arg_list.append(interpret(arg, symbol_table))
            if callable(func):
                return func(*arg_list)
            raise Exception(f"{node.name} is not a function")

        case ast.Block():
            new_scope = SymTab({}, symbol_table)
            return_val = None
            for exp in node.expressions:
                return_val = interpret(exp, new_scope)
            return return_val
    return None
