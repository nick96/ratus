import re

import pytest

from ratus.token import Token, Tokeniser, TokeniserError, TokenLiteral, TokenType


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
        ("1.0", [TokenLiteral(token_type=TokenType.FLOAT, lexeme="1.0", literal=1.0)],),
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
        ("!1", [Token(TokenType.BANG, "!"), TokenLiteral(TokenType.INT, "1", 1)],),
        pytest.param(
            "1 <= 1",
            [
                TokenLiteral(TokenType.INT, "1", 1),
                Token(TokenType.LESS_EQUAL, "<="),
                TokenLiteral(TokenType.INT, "1", 1),
            ],
            id="less_than_equal_to",
            marks=pytest.mark.xfail,
        ),
        pytest.param(
            "1 >= 1",
            [
                TokenLiteral(TokenType.INT, "1", 1),
                Token(TokenType.GREATER_EQUAL, ">="),
                TokenLiteral(TokenType.INT, "1", 1),
            ],
            id="greater_than_equal_to",
            marks=pytest.mark.xfail,
        ),
    ),
)
def test_tokenise(source, expected):
    tokeniser = Tokeniser()
    assert tokeniser.tokenise(source) == expected


@pytest.mark.parametrize(
    ("source", "error_msg"),
    (
        pytest.param(
            "'test", "Unterminated string", id="unterminated_string_single_quote",
        ),
        pytest.param(
            '"test', "Unterminated string", id="unterminated_string_double_quote",
        ),
        pytest.param(
            "1.", "Expression cannot finish with '.'", id="terminating_period"
        ),
        pytest.param("1.+1", re.escape("Expected digit after '.', found '+'")),
    ),
)
def test_tokenise_error(source, error_msg):
    tokeniser = Tokeniser()
    with pytest.raises(TokeniserError, match=error_msg):
        tokeniser.tokenise(source)
