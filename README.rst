Ratus
=====

.. image:: https://readthedocs.org/projects/ratus/badge/?version=latest
   :target: https://ratus.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

Ratus is a simple expression language that can be used to easily extend Python
applications with an embedded expression language. Evaluating basic expressions
is as simple as:

::

    from ratus import Evaluator

    evaluator = Evaluator()
    evaluator.evaluate("1 + 1") # 1
    evaluator.evaluate("1 > 1") # False
    evaluator.evaluate("if(1 < 2, 10, 5)") # 5

For more information, please check out the docs_

.. _docs: https://ratus.readthedocs.io/en/latest/
