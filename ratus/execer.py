from ratus.parse import (
    Expression,
    Literal,
    BinaryOp,
    BinaryOpType,
    UnaryOp,
    UnaryOpType,
    Function,
)
from typing import Any, Dict, Callable, Optional
import operator


class ExecutorError(Exception):
    """Exception raised if there is an error executing an expression."""


class Executor:
    """Executor of expressions."""

    def __init__(
        self, injected_functions: Optional[Dict[str, Callable[..., Any]]] = None
    ) -> None:
        self.binary_ops = {
            "+": operator.add,
            "-": operator.sub,
            "*": operator.mul,
            "/": operator.truediv,
            ">": operator.gt,
            ">=": operator.ge,
            "<": operator.lt,
            "<=": operator.le,
            "and": operator.and_,
            "or": operator.or_,
            "=": operator.eq,
            "!=": operator.ne,
        }
        self.unary_ops = {"!": operator.not_, "-": operator.neg}
        self.functions = {"if": lambda c, s, f: s if c else f}
        if injected_functions is not None:
            self.functions.update(injected_functions)

    def execute(self, expression: Expression) -> Any:
        """Execute an expression and return the result."""
        if isinstance(expression, Literal):
            return expression.value
        if isinstance(expression, BinaryOp):
            left = self.execute(expression.left)
            right = self.execute(expression.right)
            op = self.binary_ops[expression.op_type.value]
            return op(left, right)
        if isinstance(expression, UnaryOp):
            operand = self.execute(expression.operand)
            op = self.unary_ops[expression.op_type.value]
            return op(operand)
        if isinstance(expression, Function):
            function = self.functions.get(expression.name)
            if function is None:
                raise ExecutorError(f"Function '{expression.name}' is not defined")
            args = [self.execute(arg) for arg in expression.args]
            return function(*args)
