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
