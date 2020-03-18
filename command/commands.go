package command

import (
	"fmt"
	"os"

	"github.com/nick96/ratus/executor"
	"github.com/nick96/ratus/parser"
	"github.com/nick96/ratus/tokeniser"
)

var (
	ErrNotImplemented = fmt.Errorf("Not implemented")
)

func Parse(fileName string) (*parser.AST, error) {
	fh, err := os.Open(fileName)
	if err != nil {
		return nil, err
	}
	defer fh.Close()

	tokens, err := tokeniser.Tokenise(fh)
	if err != nil {
		return nil, err
	}
	ast, err := parser.Parse(tokens)
	if err != nil {
		return nil, err
	}
	return ast, nil
}

func Check(fileName string) error {
	return ErrNotImplemented
}

func Run(fileName string) (string, error) {
	ast, err := Parse(fileName)
	if err != nil {
		return "", err
	}
	result, err := executor.Exec(ast)
	if err != nil {
		return "", err
	}

	return result.AsString(), nil
}
