import argparse
from arithmetic_compiler import ArithmeticCompiler
from instructions.infix_expression_calculator_instruction import InfixExpressionCalculatorInstruction

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Arithmetic Expression Compiler CLI")
    parser.add_argument("expression", type=str, help="The arithmetic expression to compile")
    parser.add_argument("--format", type=str, choices=["json", "jsonl", "llama2", "qa"], default="json",
                        help="The output format")
    parser.add_argument("--instruction", type=str, help="Specific instruction to generate")
    parser.add_argument("--mode", type=str, choices=["tokens", "ast"], default="ast",
                        help="Choose to use 'tokens' or 'ast' form for output")
    parser.add_argument("--minimal-parentheses", action="store_true",
                        help="Use minimal parentheses in AST mode")

    # Parse arguments
    args = parser.parse_args()

    # Initialize the compiler with the provided expression
    compiler = ArithmeticCompiler(args.expression)

    # Run the compilation process
    compiler.parse_expression()

    # Generate instructions
    compiler.generate_instruction()

    # Emit output based on the requested format and mode
    if compiler.instruction:
        if args.format == "json":
            output = compiler.instruction.emit_json(args.mode, args.minimal_parentheses)
        elif args.format == "jsonl":
            output = compiler.instruction.emit_jsonl(args.mode, args.minimal_parentheses)
        elif args.format == "llama2":
            output = compiler.instruction.emit_llama2(args.mode, args.minimal_parentheses)
        elif args.format == "qa":
            output = compiler.instruction.emit_qa(args.mode, args.minimal_parentheses)

        print(f"\nInstruction in {args.format.upper()} format:")
        print(output)
    else:
        print("Failed to generate instruction.")

if __name__ == "__main__":
    main()
