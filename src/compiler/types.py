from dataclasses import dataclass
from typing import Self


@dataclass
class Type:
    """Base class for all types"""

    name: str

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.__str__()


Int: Type = Type("Int")

Bool: Type = Type("Bool")

Unit: Type = Type("Unit")


@dataclass
class FunType(Type):
    args: list[Type]
    ret: Type

    def __init__(self, args: list[Type], ret: Type) -> None:
        self.name = f'({", ".join(map(str, args))}) => {ret}'
        self.args = args
        self.ret = ret


@dataclass
class TypeTab:
    locals: dict[str, Type]
    parent: Self | None


top_level: TypeTab = TypeTab(
    {
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
