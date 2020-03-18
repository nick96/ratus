package parser

import (
	"fmt"

	"github.com/nick96/ratus/tokeniser"
)

var (
	ErrNotImplemented = fmt.Errorf("Not implemented")
)

type AST struct{}

func Parse(tokens []tokeniser.Token) (*AST, error) {
	return nil, ErrNotImplemented
}
