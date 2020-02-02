"""
Grammar
=======

These are the rules for producing a valid stream of tokens. This is what the
parser is built off.

```
Expression -> Term (("+" | "-") Term)* | Expression (">" | ">=" | "<" | "<=" | "=" | "!=") Expression  | String | Function
Term -> Factor (("*" | "/") Factor)*
Factor -> "(" Expression ")" | Number
Number -> "-"* (Integer | Float) | "!"* (Integer | Float)
Function -> Ident"(" Expression("," Expression)*")"
```

"""

from dataclasses import dataclass
from typing import List, Dict, Any, Union, Optional, Tuple
from abc import ABC
from enum import Enum

from ratus.token import Token, TokenType


class ParserError(Exception):
    """Exception raised when there is an error parsing."""


class Expression(ABC):
    """Base representation of an expression."""


class Literal(Expression, ABC):
    pass


@dataclass
class Integer(Literal):
    value: int


@dataclass
class Float(Literal):
    value: float


@dataclass
class String(Literal):
    value: str


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
    NOT = "!"
    NEGATIVE = "-"


@dataclass
class UnaryOp(ABC):
    op_type: UnaryOpType
    operand: Expression


def parse(tokens: List[Token]) -> Expression:
    expression, _ = parse_expression(tokens)
    return expression


def parse_expression(tokens: List[Token]) -> Tuple[Expression, List[Token]]:
    if len(tokens) == 0:
        raise ParserError("Expression cannot be empty")
    if tokens[0].token_type is TokenType.STRING:
        return String(tokens[0].literal), tokens[1:]
    if tokens[0].token_type is TokenType.IDENT:
        return parse_function(tokens)
    expr, rest = parse_term(tokens)
    while len(rest) > 0:
        operator, *rest = rest
        if operator.token_type not in (
            TokenType.PLUS,
            TokenType.MINUS,
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
            TokenType.LESS,
            TokenType.LESS_EQUAL,
            TokenType.EQUAL,
            TokenType.BANG_EQUAL,
            TokenType.AND,
            TokenType.OR,
        ):
            raise ParserError(
                f"Unexpected token after term {expr}. Expected operator '+', "
                "'-', '>', '>='. '<'. '<=', '=', '!=', 'and', 'or'."
            )
        right_term, rest = parse_term(rest)
        operator_type_mapping = {
            TokenType.PLUS: BinaryOpType.ADDITION,
            TokenType.MINUS: BinaryOpType.SUBTRACTION,
            TokenType.GREATER: BinaryOpType.GREATER,
            TokenType.GREATER_EQUAL: BinaryOpType.GREATER_EQUAL,
            TokenType.LESS: BinaryOpType.LESS,
            TokenType.LESS_EQUAL: BinaryOpType.LESS_EQUAL,
            TokenType.EQUAL: BinaryOpType.EQUAL,
            TokenType.BANG_EQUAL: BinaryOpType.NOT_EQUAL,
            TokenType.AND: BinaryOpType.AND,
            TokenType.OR: BinaryOpType.OR,
        }
        operator_type = operator_type_mapping[operator.token_type]
        expr = BinaryOp(operator_type, expr, right_term)
    return expr, []


def parse_function(tokens: List[Token]) -> Tuple[Expression, List[Token]]:
    if len(tokens) < 3:
        raise ParserError(f"Tokens {tokens} do not form a valid function call")
    if tokens[1].token_type is not TokenType.LEFT_PAREN:
        raise ParserError(
            f"Expected left paren ('(') following call to function '{tokens[0].literal}'. Found '{tokens[1].lexeme}'"
        )
    nesting = 0
    end_of_function_call_idx = 0
    for i, token in enumerate(tokens):
        if token.token_type is TokenType.LEFT_PAREN:
            nesting += 1
        elif token.token_type is TokenType.RIGHT_PAREN:
            nesting -= 1
            if nesting == 0:
                end_of_function_call_idx = i
                break
    else:
        raise ParserError(
            f"Unbalanced parentheses in call to function '{tokens[0].literal}'"
        )
    name = tokens[0].literal
    if len(tokens) == 3:
        return Function(name, args=[]), tokens[end_of_function_call_idx + 1 :]
    args_tokens, rest = split_function_args(tokens[2:])
    args = [parse(arg_tokens) for arg_tokens in args_tokens]
    return Function(name, args=args), rest


def parse_term(tokens: List[Token]) -> Tuple[Expression, List[Token]]:
    term, rest = parse_factor(tokens)
    while len(rest) > 0:
        operator, *rest = rest
        if operator.token_type not in (TokenType.STAR, TokenType.SLASH):
            return term, [operator] + rest

        # Based on the condition we know the operator token is STAR or SLASH
        right_factor, rest = parse_factor(rest)
        operator_type_mapping = {
            TokenType.STAR: BinaryOpType.MULTIPLICATION,
            TokenType.SLASH: BinaryOpType.DIVISION,
        }
        operator_type = operator_type_mapping[operator.token_type]
        term = BinaryOp(operator_type, term, right_factor)

    return term, rest


def parse_factor(tokens: List[Token]) -> Tuple[Expression, List[Token]]:
    if tokens[0].token_type is TokenType.LEFT_PAREN:
        expr_end_index = 0
        nesting = 0
        for i, token in enumerate(tokens):
            if token.token_type is TokenType.LEFT_PAREN:
                nesting += 1
            elif token.token_type is TokenType.RIGHT_PAREN:
                nesting -= 1
                if nesting == 0:
                    expr_end_index = i
                    break
        expr_tokens = tokens[1:expr_end_index]
        expr = parse(expr_tokens)
        return expr, tokens[expr_end_index + 1 :]
    return parse_number(tokens)


def parse_number(
    tokens: List[Token], bang_allowed=True, minus_allowed=True
) -> Tuple[Expression, List[Token]]:
    if len(tokens) == 0:
        raise ParserError(f"Expected int or float token but none were found")
    if tokens[0].token_type is TokenType.INT:
        return Integer(tokens[0].literal), tokens[1:]
    if tokens[0].token_type is TokenType.FLOAT:
        return Float(tokens[0].literal), tokens[1:]
    if tokens[0].token_type is TokenType.MINUS and minus_allowed:
        operand, rest = parse_number(tokens[1:], bang_allowed=False)
        return UnaryOp(UnaryOpType.NEGATIVE, operand), rest
    if tokens[0].token_type is TokenType.BANG and bang_allowed:
        operand, rest = parse_number(tokens[1:], minus_allowed=False)
        return UnaryOp(UnaryOpType.NOT, operand), rest
    raise ParserError(f"Unexpected token {tokens[0]}. Expected an int or float")


def split_function_args(tokens: List[Token]) -> Tuple[List[List[Token]], List[Token]]:
    nesting = 1
    arg: List[Token] = []
    function_args: List[List[Token]] = []
    while len(tokens) > 0:
        token = tokens.pop(0)
        if token.token_type is TokenType.LEFT_PAREN:
            nesting += 1
        elif token.token_type is TokenType.RIGHT_PAREN:
            nesting -= 1
            if nesting == 0:
                function_args.append(arg)
                return function_args, tokens

        if nesting == 1 and token.token_type is TokenType.COMMA:
            function_args.append(arg)
            arg = []
        else:
            arg.append(token)
    raise ParserError("Function call does not have closing paren (')')")


class Parser:
    def parse(self, tokens: List[Token]):
        return parse(tokens)
