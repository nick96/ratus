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
from typing import Any

from ratus.exec import Executor
from ratus.parse import Parser, ParserError
from ratus.token import Tokeniser, TokeniserError

__version__ = "0.0.1"


def evaluate(input_: str) -> Any:
    """Evaluate an input as a ratus expression."""
    tokeniser = Tokeniser(input_)
    tokens = tokeniser.tokenise(input_)

    parser = Parser(tokens)
    expr = parser.parse()

    executor = Executor(expr)
    return executor.execute()
