from dataclasses import dataclass
from typing import Self


class Type:
    """Base class for all types"""


Int: Type = Type()

Bool: Type = Type()

Unit: Type = Type()


@dataclass
class FunType(Type):
    args: list[Type]
    ret: Type


@dataclass
class TypeTab:
    locals: dict[str, Type]
    parent: Self | None


top_level: TypeTab = TypeTab(
    {
        "true": Bool,
        "false": Bool,
        "unit": Unit,
        "+": FunType(args=[Int, Int], ret=Int),
        "-": FunType([Int, Int], Int),
        "*": FunType([Int, Int], Int),
        "/": FunType([Int, Int], Int),
        "%": FunType([Int, Int], Int),
        "<": FunType([Int, Int], Bool),
        "<=": FunType([Int, Int], Bool),
        ">": FunType([Int, Int], Bool),
        ">=": FunType([Int, Int], Bool),
        "or": FunType([Bool, Bool], Bool),
        "and": FunType([Bool, Bool], Bool),
        "unary_-": FunType([Int], Int),
        "unary_not": FunType([Bool], Bool),
        "print_int": FunType([Int], Unit),
        "print_bool": FunType([Bool], Unit),
    },
    None,
)
