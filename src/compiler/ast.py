from dataclasses import dataclass


@dataclass
class Expression:
    """Base class for AST nodes representing expressions."""


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
class Block(Expression):
    expressions: list[Expression]


@dataclass
class While(Expression):
    condition: Expression
    block: Block
