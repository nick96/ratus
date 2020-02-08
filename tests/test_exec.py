import operator

import pytest

from ratus.execer import Executor
from ratus.parse import BinaryOp, BinaryOpType, Function, Integer, UnaryOp, UnaryOpType


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
    ("expression", "binary_op_overrides", "expected"),
    (
        (
            BinaryOp(BinaryOpType.ADDITION, Integer(1), Integer(1)),
            {BinaryOpType.ADDITION: operator.sub},
            0,
        ),
        (
            BinaryOp(BinaryOpType.SUBTRACTION, Integer(1), Integer(1)),
            {BinaryOpType.SUBTRACTION: operator.add},
            2,
        ),
        (
            BinaryOp(BinaryOpType.MULTIPLICATION, Integer(1), Integer(1)),
            {BinaryOpType.MULTIPLICATION: operator.le},
            True,
        ),
    ),
)
def test_override_binary_ops(expression, binary_op_overrides, expected):
    executor = Executor(binary_ops=binary_op_overrides)
    assert executor.execute(expression) == expected


@pytest.mark.parametrize(
    ("expression", "unary_op_overrides", "expected"),
    (
        (UnaryOp(UnaryOpType.NOT, Integer(1)), {UnaryOpType.NOT: operator.neg}, -1,),
        (
            UnaryOp(UnaryOpType.NEGATIVE, Integer(1)),
            {UnaryOpType.NEGATIVE: operator.not_},
            False,
        ),
    ),
)
def test_override_unary_ops(expression, unary_op_overrides, expected):
    executor = Executor(unary_ops=unary_op_overrides)
    assert executor.execute(expression) == expected
