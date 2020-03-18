package command

import (
	"fmt"
	"github.com/nick96/ratus/parse"
)

var (
	ErrNotImplemented = fmt.Errorf("Not implemented")
)

func Parse(fileName string) (*parse.AST, error) {
	return nil, ErrNotImplemented
}

func Check(fileName string) error {
	return ErrNotImplemented
}

func Run(fileName string) (string, error) {
	return "", ErrNotImplemented
}
