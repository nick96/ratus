import re

import pytest

from ratus.parse import (
    BinaryOp,
    BinaryOpType,
    Float,
    Function,
    Integer,
    Parser,
    ParserError,
    String,
    UnaryOp,
    UnaryOpType,
)
from ratus.token import Token, TokenLiteral, TokenType


@pytest.mark.parametrize(
    ("tokens", "expected"),
    (
        pytest.param(
            [TokenLiteral(TokenType.INT, "1", 1)], Integer(1), id="int-literal"
        ),
        pytest.param(
            [TokenLiteral(TokenType.FLOAT, "1.0", 1.0)], Float(1.0), id="float-literal",
        ),
        pytest.param(
            [TokenLiteral(TokenType.STRING, '"test"', "test")],
            String("test"),
            id="string-literal",
        ),
        pytest.param(
            [Token(TokenType.MINUS, "-"), TokenLiteral(TokenType.INT, "1", 1)],
            UnaryOp(UnaryOpType.NEGATIVE, Integer(1)),
            id="negative-int-literal",
        ),
        pytest.param(
            [Token(TokenType.MINUS, "-"), TokenLiteral(TokenType.FLOAT, "1.0", 1.0),],
            UnaryOp(UnaryOpType.NEGATIVE, Float(1.0)),
            id="negative-float-literal",
        ),
        pytest.param(
            [
                TokenLiteral(TokenType.INT, "1", 1),
                Token(TokenType.PLUS, "+"),
                TokenLiteral(TokenType.INT, "1", 1),
            ],
            BinaryOp(BinaryOpType.ADDITION, Integer(1), Integer(1)),
            id="int-addition",
        ),
        pytest.param(
            [Token(TokenType.BANG, "!"), TokenLiteral(TokenType.INT, "1", 1)],
            UnaryOp(UnaryOpType.NOT, Integer(1)),
            id="int-negate",
        ),
        pytest.param(
            [
                TokenLiteral(TokenType.INT, "1", 1),
                Token(TokenType.GREATER, ">"),
                TokenLiteral(TokenType.INT, "2", 2),
            ],
            BinaryOp(BinaryOpType.GREATER, Integer(1), Integer(2)),
            id="greater-than",
        ),
        pytest.param(
            [
                TokenLiteral(TokenType.IDENT, "if", "if"),
                Token(TokenType.LEFT_PAREN, "("),
                TokenLiteral(TokenType.INT, "1", 1),
                Token(TokenType.GREATER, ">"),
                TokenLiteral(TokenType.INT, "2", 2),
                Token(TokenType.COMMA, ","),
                TokenLiteral(TokenType.INT, "1", 1),
                Token(TokenType.COMMA, ","),
                TokenLiteral(TokenType.INT, "2", 2),
                Token(TokenType.RIGHT_PAREN, ")"),
            ],
            Function(
                "if",
                [
                    BinaryOp(BinaryOpType.GREATER, Integer(1), Integer(2)),
                    Integer(1),
                    Integer(2),
                ],
            ),
            id="function-call",
        ),
        pytest.param(
            [
                Token(TokenType.LEFT_PAREN, "("),
                TokenLiteral(TokenType.INT, "1", 1),
                Token(TokenType.PLUS, "+"),
                TokenLiteral(TokenType.INT, "2", 2),
                Token(TokenType.RIGHT_PAREN, ")"),
                Token(TokenType.STAR, "*"),
                TokenLiteral(TokenType.INT, "3", 3),
            ],
            BinaryOp(
                BinaryOpType.MULTIPLICATION,
                BinaryOp(BinaryOpType.ADDITION, Integer(1), Integer(2)),
                Integer(3),
            ),
            id="grouping",
        ),
        pytest.param(
            [
                TokenLiteral(TokenType.IDENT, "if", "if"),
                Token(TokenType.LEFT_PAREN, "("),
                TokenLiteral(TokenType.IDENT, "if", "if"),
                Token(TokenType.LEFT_PAREN, "("),
                TokenLiteral(TokenType.INT, "1", 1),
                Token(TokenType.GREATER, ">"),
                TokenLiteral(TokenType.INT, "2", 2),
                Token(TokenType.COMMA, ","),
                TokenLiteral(TokenType.INT, "1", 1),
                Token(TokenType.COMMA, ","),
                TokenLiteral(TokenType.INT, "0", 0),
                Token(TokenType.RIGHT_PAREN, ")"),
                Token(TokenType.COMMA, ","),
                TokenLiteral(TokenType.INT, "0", 0),
                Token(TokenType.COMMA, ","),
                TokenLiteral(TokenType.INT, "1", 1),
                Token(TokenType.RIGHT_PAREN, ")"),
            ],
            Function(
                "if",
                args=[
                    Function(
                        "if",
                        args=[
                            BinaryOp(BinaryOpType.GREATER, Integer(1), Integer(2)),
                            Integer(1),
                            Integer(0),
                        ],
                    ),
                    Integer(0),
                    Integer(1),
                ],
            ),
            id="nested-function-call",
        ),
        pytest.param(
            [
                TokenLiteral(TokenType.IDENT, "f", "f"),
                Token(TokenType.LEFT_PAREN, "("),
                Token(TokenType.RIGHT_PAREN, ")"),
            ],
            Function("f", args=[]),
            id="function-call-no-args",
        ),
    ),
)
def test_parse(tokens, expected):
    parser = Parser()
    assert parser.parse(tokens) == expected


@pytest.mark.parametrize(
    ("tokens", "error_msg"),
    (
        pytest.param([], "Expression cannot be empty", id="empty_expression"),
        pytest.param(
            [TokenLiteral(TokenType.IDENT, "f", "f")],
            re.escape(
                f"Tokens {[TokenLiteral(TokenType.IDENT, 'f', 'f')]} do not"
                " form a valid function call"
            ),
            id="invalid_function_call",
        ),
        pytest.param(
            [
                TokenLiteral(TokenType.IDENT, "f", "f"),
                TokenLiteral(TokenType.INT, "1", 1),
                Token(TokenType.COMMA, ","),
                Token(TokenType.RIGHT_PAREN, ")"),
            ],
            re.escape(
                f"Expected left paren ('(') following call to function 'f'. "
                "Found '1'"
            ),
            id="unbalanced_closing_paren",
        ),
        pytest.param(
            [TokenLiteral(TokenType.INT, "1", 1), Token(TokenType.LEFT_PAREN, "("),],
            re.escape(
                f"Unexpected token after term {Integer(1)}. "
                "Expected operator '+', "
                "'-', '>', '>=', '<', '<=', '=', '!=', 'and', 'or'."
            ),
            id="unexpected_term_after_literal",
        ),
        pytest.param(
            [
                TokenLiteral(TokenType.IDENT, "f", "f"),
                Token(TokenType.LEFT_PAREN, "("),
                Token(TokenType.LEFT_PAREN, "("),
                TokenLiteral(TokenType.INT, "1", 1),
                Token(TokenType.RIGHT_PAREN, ")"),
            ],
            re.escape("Unbalanced parentheses in call to function 'f'"),
            id="unbalanced_opening_paren_in_func",
        ),
        pytest.param(
            [Token(TokenType.PLUS, "+"), TokenLiteral(TokenType.INT, "1", 1)],
            re.escape(
                f"Unexpected token {Token(TokenType.PLUS, '+')}."
                " Expected an int or float"
            ),
        ),
    ),
)
def test_parser_error(tokens, error_msg):
    parser = Parser()
    with pytest.raises(ParserError, match=error_msg):
        parser.parse(tokens)
