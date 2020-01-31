from dataclasses import dataclass
from typing import List, Dict, Any, Union
from abc import ABC
from enum import Enum

from ratus.token import Token, TokenType


class ParserError(Exception):
    """Exception raised when there is an error parsing."""


class Expression(ABC):
    """Base representation of an expression."""


@dataclass
class Literal:
    value: Union[str, int, float]


@dataclass
class Function:
    name: str
    args: List[Expression]


class BinaryOpType(Enum):
    ADDITION = "+"
    SUBTRACTION = "-"
    MULTIPLICATION = "*"
    DIVISION = "/"
    EQUAL = "="
    NOT_EQUAL = "!="
    GREATER = ">"
    GREATER_EQUAL = ">="
    LESS = "<"
    LESS_EQUAL = "<="
    AND = "and"
    OR = "or"


@dataclass
class BinaryOp(ABC):
    op_type: BinaryOpType
    left: Expression
    right: Expression


class UnaryOpType(Enum):
    NEGATE = "!"


@dataclass
class UnaryOp(ABC):
    op_type: UnaryOpType
    operand: Expression


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens: List[Token] = tokens
        self.current = 0
        self.match: List[Token] = []

    def parse(self):
        while self.current < len(self.tokens):
            case = {}
