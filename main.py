import argparse
import re
from compiler.arithmetic_compiler import ArithmeticCompiler


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Arithmetic Expression Compiler CLI")

    # Get the expression
    parser.add_argument("expression", type=str, help="The arithmetic expression to compile")

    # Output format
    parser.add_argument("--format", type=str, choices=["json", "jsonl", "llama2", "qa", "pretty", "step-by-step", "chat"], default="json",
                        help="The output format")

    # Specify language model
    parser.add_argument("--llm", type=str, default=None, help="Specify the name of the language model to use")

    # Parse arguments
    args = parser.parse_args()

    # Set default LLM if required by the format and not specified
    if args.format in ["pretty", "step-by-step"] and not args.llm:
        args.llm = "mistral-nemo"

    # Initialize the compiler with the provided expression
    compiler = ArithmeticCompiler(args.expression)

    # Run the compilation process
    compiler.parse_expression()

    # Generate instructions
    compiler.generate_instruction(args.llm)

    # Function to strip control characters but keep newlines and carriage returns
    def strip_control_characters(text):
        return re.sub(r'[^\x20-\x7E\n\r]', '', text)

    # Function to replace LaTeX-style expressions with plain text
    def replace_latex_symbols(text):
        return (text
                .replace(r'\(', '')
                .replace(r'\)', '')
                .replace(r'\[', '')
                .replace(r'\]', '')
                .replace(r'\times', '*'))

    # Emit output based on the requested format and mode
    if compiler.instruction:
        # Get the full instruction output
        instruction_output = compiler.instruction.emit_instruction()

        if args.format == "pretty":
            # Print question and pretty result
            print("\nPretty Result:")
            print(strip_control_characters(replace_latex_symbols(instruction_output["instruction"])))
            print(strip_control_characters(replace_latex_symbols(instruction_output["llm_pretty_result"])))
        elif args.format == "step-by-step":
            # Print question and step-by-step result
            print("\nStep-by-Step Explanation:")
            print(strip_control_characters(replace_latex_symbols(instruction_output["instruction"])))
            print(strip_control_characters(replace_latex_symbols(instruction_output["llm_step_by_step_result"])))
        elif args.format == "json":
            # Emit JSON
            output = compiler.instruction.emit_json()
            print(f"\nInstruction in {args.format.upper()} format:")
            print(output)
        elif args.format == "jsonl":
            # Emit JSONL
            output = compiler.instruction.emit_jsonl()
            print(f"\nInstruction in {args.format.upper()} format:")
            print(output)
        elif args.format == "chat":
            # Emit JSONL
            output = compiler.instruction.emit_chat()
            print(f"\nInstruction in {args.format.upper()} format:")
            print(output)
        elif args.format == "llama2":
            # Emit llama2
            output = compiler.instruction.emit_llama2()
            print(f"\nInstruction in {args.format.upper()} format:")
            print(output)
        elif args.format == "qa":
            # Emit QA format
            output = compiler.instruction.emit_qa()
            print(f"\nInstruction in {args.format.upper()} format:")
            print(output)
    else:
        print("Failed to generate instruction.")

if __name__ == "__main__":
    main()
