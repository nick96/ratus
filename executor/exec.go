package executor

import (
	"fmt"

	"github.com/zclconf/go-cty/cty"

	"github.com/nick96/ratus/parser"
)

func Exec(ast *parser.AST) (cty.Value, error) {
	return cty.NullVal(cty.EmptyObject), fmt.Errorf("Not implemented")
}
