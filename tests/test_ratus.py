import re

import pytest

from ratus import Evaluator, __version__
from ratus.execer import Executor, ExecutorError
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
from ratus.token import Token, Tokeniser, TokenLiteral, TokenType


def test_version():
    assert __version__ == "0.0.1"


@pytest.mark.parametrize(
    ("source", "expected"),
    (
        ("1", [TokenLiteral(token_type=TokenType.INT, lexeme="1", literal=1)]),
        (
            "'test'",
            [
                TokenLiteral(
                    token_type=TokenType.STRING, lexeme="'test'", literal="test"
                )
            ],
        ),
        (
            '"test"',
            [
                TokenLiteral(
                    token_type=TokenType.STRING, lexeme='"test"', literal="test"
                )
            ],
        ),
        ("1.0", [TokenLiteral(token_type=TokenType.FLOAT, lexeme="1.0", literal=1.0)]),
        (
            "-1",
            [
                Token(TokenType.MINUS, "-"),
                TokenLiteral(token_type=TokenType.INT, lexeme="1", literal=1),
            ],
        ),
        (
            "-1.0",
            [
                Token(TokenType.MINUS, "-"),
                TokenLiteral(token_type=TokenType.FLOAT, lexeme="1.0", literal=1.0),
            ],
        ),
        (
            "1 + 1",
            [
                TokenLiteral(TokenType.INT, "1", 1),
                Token(TokenType.PLUS, "+"),
                TokenLiteral(TokenType.INT, "1", 1),
            ],
        ),
        (
            "1 - 1",
            [
                TokenLiteral(TokenType.INT, "1", 1),
                Token(TokenType.MINUS, "-"),
                TokenLiteral(TokenType.INT, "1", 1),
            ],
        ),
        (
            "1 + 3 * 2",
            [
                TokenLiteral(TokenType.INT, "1", 1),
                Token(TokenType.PLUS, "+"),
                TokenLiteral(TokenType.INT, "3", 3),
                Token(TokenType.STAR, "*"),
                TokenLiteral(TokenType.INT, "2", 2),
            ],
        ),
        ("2.0", [TokenLiteral(TokenType.FLOAT, "2.0", 2.0)]),
        ('"test"', [TokenLiteral(TokenType.STRING, '"test"', "test")]),
        (
            "if(1 > 2, 10, 5)",
            [
                TokenLiteral(TokenType.IDENT, "if", "if"),
                Token(TokenType.LEFT_PAREN, "("),
                TokenLiteral(TokenType.INT, "1", 1),
                Token(TokenType.GREATER, ">"),
                TokenLiteral(TokenType.INT, "2", 2),
                Token(TokenType.COMMA, ","),
                TokenLiteral(TokenType.INT, "10", 10),
                Token(TokenType.COMMA, ","),
                TokenLiteral(TokenType.INT, "5", 5),
                Token(TokenType.RIGHT_PAREN, ")"),
            ],
        ),
        (
            "if(1<2, 10, 5)",
            [
                TokenLiteral(TokenType.IDENT, "if", "if"),
                Token(TokenType.LEFT_PAREN, "("),
                TokenLiteral(TokenType.INT, "1", 1),
                Token(TokenType.LESS, "<"),
                TokenLiteral(TokenType.INT, "2", 2),
                Token(TokenType.COMMA, ","),
                TokenLiteral(TokenType.INT, "10", 10),
                Token(TokenType.COMMA, ","),
                TokenLiteral(TokenType.INT, "5", 5),
                Token(TokenType.RIGHT_PAREN, ")"),
            ],
        ),
    ),
)
def test_tokenise(source, expected):
    tokeniser = Tokeniser()
    assert tokeniser.tokenise(source) == expected


@pytest.mark.parametrize(("source", "error_msg"), ())
def test_tokenise_error(source, error_msg):
    pass


@pytest.mark.parametrize(
    ("tokens", "expected"),
    (
        pytest.param(
            [TokenLiteral(TokenType.INT, "1", 1)], Integer(1), id="int-literal"
        ),
        pytest.param(
            [TokenLiteral(TokenType.FLOAT, "1.0", 1.0)], Float(1.0), id="float-literal"
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
            [Token(TokenType.MINUS, "-"), TokenLiteral(TokenType.FLOAT, "1.0", 1.0)],
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
                f"Tokens {[TokenLiteral(TokenType.IDENT, 'f', 'f')]} do not form a valid function call"
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
                f"Expected left paren ('(') following call to function 'f'. Found '1'"
            ),
        ),
    ),
)
def test_parser_error(tokens, error_msg):
    parser = Parser()
    with pytest.raises(ParserError, match=error_msg):
        parser.parse(tokens)


@pytest.mark.parametrize(
    ("expression", "expected"),
    (
        (Integer(1), 1),
        (BinaryOp(BinaryOpType.ADDITION, Integer(1), Integer(1)), 2),
        (UnaryOp(UnaryOpType.NOT, Integer(1)), False),
        (
            BinaryOp(
                BinaryOpType.MULTIPLICATION,
                BinaryOp(BinaryOpType.ADDITION, Integer(1), Integer(2)),
                Integer(3),
            ),
            9,
        ),
        (
            Function(
                "if",
                [
                    BinaryOp(BinaryOpType.GREATER, Integer(1), Integer(2)),
                    Integer(1),
                    Integer(2),
                ],
            ),
            2,
        ),
    ),
)
def test_execute(expression, expected):
    executor = Executor()
    assert executor.execute(expression) == expected


@pytest.mark.parametrize(
    ("source", "expected", "injected_functions"),
    (
        pytest.param("1 + 1", 2, None, id="addition"),
        pytest.param("1 - 1", 0, None, id="subtraction"),
        pytest.param("1 + 3 * 2", 7, None, id="precedence"),
        pytest.param("2.0", 2.0, None, id="float_literal"),
        pytest.param('"test"', "test", None, id="string_literal"),
        pytest.param("if(1 > 2, 10, 5)", 5, None, id="false_conditional"),
        pytest.param("if(1<2, 10, 5)", 10, None, id="true_conditional"),
        pytest.param("if(if(1<2, 0, 1), 10, 5)", 5, None, id="nested_conditional"),
        pytest.param("2 + 3 * 2", 8, None, id="bodmas"),
        pytest.param("3 * 2 + 2", 8, None, id="computation_ordering"),
        pytest.param("1 > 2", False, None, id="greater_than"),
        pytest.param("1 = 1", True, None, id="equals"),
        pytest.param("1 != 2", True, None, id="not_equals"),
        pytest.param(
            "lookup(12345, 'PG')",
            10,
            {"lookup": lambda x, y: 10},
            id="injected_function",
        ),
        pytest.param(
            "if(lookup(12345, 'PG') = 10, 5, 4)",
            5,
            {"lookup": lambda x, y: 10},
            id="injected_function_in_conditional",
        ),
        pytest.param(
            "add(1, 2)",
            3,
            {"add": lambda x, y: x + y},
            id="function_call_in_computation",
        ),
    ),
)
def test_eval(source, expected, injected_functions):
    evaluator = Evaluator(injected_functions)
    assert evaluator.evaluate(source) == expected


@pytest.mark.parametrize(
    ("source", "injected_functions", "error_msg"),
    (("test(1, 2)", None, "Function 'test' is not defined"),),
)
def test_eval_error(source, injected_functions, error_msg):
    evaluator = Evaluator(injected_functions)
    with pytest.raises(ExecutorError, match=error_msg):
        evaluator.evaluate(source)
