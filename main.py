import argparse
from compiler.arithmetic_compiler import ArithmeticCompiler
from compiler.instructions.infix_expression_calculator_instruction import InfixExpressionCalculatorInstruction

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Arithmetic Expression Compiler CLI")

    # get the expression
    parser.add_argument("expression", type=str, help="The arithmetic expression to compile")

    # output format
    parser.add_argument("--format", type=str, choices=["json", "jsonl", "llama2", "qa"], default="json",
                        help="The output format")
    
    # the instruction we want to generate
    parser.add_argument("--instruction", type=str, help="Specific instruction to generate")
    
    # specify language model
    parser.add_argument("--llm", type=str, default=None, help="Specify the name of the language model to use")

    # Parse arguments
    args = parser.parse_args()

    # Initialize the compiler with the provided expression
    compiler = ArithmeticCompiler(args.expression)

    # Run the compilation process
    compiler.parse_expression()

    # Generate instructions
    compiler.generate_instruction(args.llm)

    # Emit output based on the requested format and mode
    if compiler.instruction:
        if args.format == "json":
            # emit json
            output = compiler.instruction.emit_json()
        elif args.format == "jsonl":
            # emit jsonl
            output = compiler.instruction.emit_jsonl()
        elif args.format == "llama2":
            # emit llama2
            output = compiler.instruction.emit_llama2()
        elif args.format == "qa":
            # emit qa format
            output = compiler.instruction.emit_qa()

        print(f"\nInstruction in {args.format.upper()} format:")
        print(output)
    else:
        print("Failed to generate instruction.")

if __name__ == "__main__":
    main()
