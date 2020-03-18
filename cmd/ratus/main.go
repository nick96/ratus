package main

import (
	"fmt"
	"os"

	"github.com/nick96/ratus/command"
	"github.com/spf13/cobra"
)

var (
	// Version is the built version of ratus.
	Version string
	// Commit is the commit SHA used to build the binary.
	Commit string
)

func main() {
	cmdParse := &cobra.Command{
		Use:   "parse",
		Short: "Parse a ratus file and output the AST representation.",
		Args:  cobra.MinimumNArgs(1),
		Run: func(cmd *cobra.Command, args []string) {
			ast, err := command.Parse(args[0])
			if err != nil {
				fmt.Fprintln(os.Stderr, "Error:", err)
				os.Exit(1)
			}
			fmt.Println(ast)
		},
	}
	cmdCheck := &cobra.Command{
		Use:   "check",
		Short: "Check a ratus file.",
		Args:  cobra.MaximumNArgs(1),
		Run: func(cmd *cobra.Command, args []string) {
			if err := command.Check(args[0]); err != nil {
				fmt.Fprintln(os.Stderr, "Error:", err)
				os.Exit(1)
			}
		},
	}
	cmdRun := &cobra.Command{
		Use:   "run",
		Short: "Run a ratus file.",
		Args:  cobra.MinimumNArgs(1),
		Run: func(cmd *cobra.Command, args []string) {
			result, err := command.Run(args[0])
			if err != nil {
				fmt.Fprintln(os.Stderr, "Error:", err)
				os.Exit(1)
			}
			fmt.Println(result)
		},
	}

	cmdRoot := &cobra.Command{
		Use:     "ratus",
		Short:   "A python-like language with structural subtyping",
		Version: Version,
	}
	cmdRoot.AddCommand(cmdParse, cmdCheck, cmdRun)
	cobra.AddTemplateFunc("Commit", func() string { return Commit })
	cmdRoot.SetVersionTemplate("{{ .Name }} {{ .Version }} {{ Commit }}\n")
	cmdRoot.Execute()
}
