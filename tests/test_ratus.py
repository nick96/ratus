import pytest

from ratus import __version__, tokenise, parse, execute, evaluate


def test_version():
    assert __version__ == "0.0.1"


@pytest.mark.parameterize(("input", "expected"), ((("1", [Integer()]))))
def test_tokenise(input_, expected):
    assert tokenise(input_) == expected


@pytest.mark.parameterize(("input_", "expected"), ())
def test_parse(input_, expected):
    assert parse(input_) == expected


@pytest.mark.parameterize(("input_", "expected"), ())
def test_execute(input_, expected):
    assert execute(input_) == expected


@pytest.mark.parameterize(
    ("input_", "expected"),
    (
        pytest.param("1 + 1", 2, id="addition"),
        pytest.param("1 - 1", 0, id="subtraction"),
        pytest.param("1 + 3 * 2", 7, id="precedence"),
        pytest.param("2.0", 2.0, id="float_literal"),
        pytest.param('"test"', "test", id="string_literal"),
        pytest.param("if(1 > 2, 10, 5)", 5, id="false_conditional"),
        pytest.param("if(1<2, 10, 5)", 10, id="true_conditional"),
    ),
)
def test_eval(input_, expected):
    assert evaluate(input_) == expected
