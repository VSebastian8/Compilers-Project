from dataclasses import dataclass, field
from compiler.token import Location, L
from compiler.types import Type, Unit


@dataclass
class Expression:
    """Base class for AST nodes representing expressions."""

    loc: Location = field(default_factory=lambda: L, kw_only=True)
    typ: Type = field(default_factory=lambda: Unit, kw_only=True)


@dataclass
class Literal(Expression):
    value: int | bool | None


@dataclass
class Identifier(Expression):
    name: str


@dataclass
class UnaryOp(Expression):
    op: str
    exp: Expression


@dataclass
class BinaryOp(Expression):
    """AST node for a binary operation like `A + B`"""

    left: Expression
    op: str
    right: Expression


@dataclass
class IfThenElse(Expression):
    condition: Expression
    then: Expression
    otherwise: Expression | None


@dataclass
class FunctionCall(Expression):
    name: str
    args: list[Expression]


@dataclass
class Assignment(Expression):
    left: str  # identifier
    right: Expression


@dataclass
class VarDec(Expression):
    left: str  # identifier
    right: Expression


@dataclass
class Block(Expression):
    expressions: list[Expression]


@dataclass
class While(Expression):
    condition: Expression
    block: Block


@dataclass
class LoopControl(Expression):
    name: str  # break or continue
