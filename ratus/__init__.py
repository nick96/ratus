"""ratus - A simple expression language.
ratus is a simple expression language intended to be used to easily and safely
extend applications in a controllable way. It provides the following features:

- Callable functions
  - These can be injected when evaluating the expression but they cannot be
    defined
  - `if` is provided by default but can be overrides if you really want to
- Simple math operations, more advanced functions can be implemented as
  functions
  - Addition (+)
  - Subtractions (-)
  - Multiplication (*)
  - Division (/)
- Comparison operators
  - Equal (=)
  - Not equal (!=)
  - Greater than (>)
  - Greater than or equal (>=)
  - Less than (<)
  - Less than or equal (<=)
- Literals
  - String (double and single quotes)
  - Integer (positive and negative)
  - Float (positive and negative)

Grammar
-------

expression -> literal | unary | binary | grouping;
literal -> int | float | string;
unary -> unary_op expression;
unary_op -> '-' | '!';
binary -> expression binary_op expression;
binary_op -> '=' | '!=' | '<' | '<=' | '>' | '>=' | '+' | '-' | '/';


Associatity
"""
from typing import Any, Optional, Dict, Callable

from ratus.execer import Executor
from ratus.parse import Parser
from ratus.token import Tokeniser

__version__ = "0.0.1"


class Evaluator:
    def __init__(
        self, injected_functions: Optional[Dict[str, Callable[..., Any]]] = None
    ) -> None:
        self.tokeniser = Tokeniser()
        self.parser = Parser()
        self.executor = Executor(injected_functions)

    def evaluate(self, source: str) -> Any:
        """Evaluate an input as a ratus expression."""
        tokens = self.tokeniser.tokenise(source)

        expression = self.parser.parse(tokens)

        return self.executor.execute(expression)
