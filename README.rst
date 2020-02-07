Ratus
=====

Ratus is a simple expression language that can be used to easily extend Python
applications with an embedded expression language. Evaluating basic expressions
is as simple as:

::

    from ratus import Evaluator

    evaluator = Evaluator()
    evaluator.evaluate("1 + 1") # 1
    evaluator.evaluate("1 > 1") # False
    evaluator.evaluate("if(1 < 2, 10, 5)") # 5

Expression language
-------------------

The ratus expression language allows the following constructs:

- Int, Float and String literals
- Comparison operations
  - Greater than (`>`)
  - Greater than or equal (`>=`)
  - Less than (`<`)
  - Less than or equal (`<=`)
  - Equal (`=`)
  - Not equal (`!=`)

Function injection
------------------

You can add new functions by creating the `Evaluator` object with a dictionary
argument in the constructor that maps the function name to a callable that
performs the desired behavior.

::

    from ratus import Evaluator

    def f(x):
        return x**2

    evaluator = Evaluator({
        "f": f,
        "g": lambda x: x**3
    })
    evaluator.evaluate("f(2)") # 4
    evaluator.evaluate("g(2)") # 8

Unary/Binary operation override
-------------------------------

You can override what the unary and binary operations do by providing a
dictionary as the `unary_ops` and `binary_ops` argument, respectively, to
`Evaluator`'s constructor. This will update the mapping for the specified
operations but will not change any of the others.

::

    from ratus import Evaluator, BinaryOpTypes, UnaryOpTypes

    def gt(x, y):
        return x >= y
    def neg(x):
        return x

    evaluator = Evaluator(
        binary_ops={BinaryOpTypes.GREATER: gt},
        unary_ops={UnaryOpTypes.NEGATIVE: neg}
    )
    evaluator.evaluate("-1") # 1
    evaluator.evaluate("1 > 1") # True

This is a contrived example and hopefully not something you would need to do but
it serves as an example of how you can alter the behavior of all operators.

