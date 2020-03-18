package tokeniser

import (
	"fmt"
	"io"
)

var (
	ErrNotImplemented = fmt.Errorf("Not implemented")
)

type Token struct {
	Lexeme   rune
	FileName string
	Line     int
	Column   int
}

func Tokenise(rdr io.Reader) ([]Token, error) {
	return nil, ErrNotImplemented
}
