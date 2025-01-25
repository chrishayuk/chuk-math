#!/usr/bin/env python3
import argparse
import re
from compiler.arithmetic_compiler import ArithmeticCompiler
from expression_generator.arithmetic_expression_generator import ArithmeticExpressionGenerator

def strip_control_characters(text: str) -> str:
    """
    Strips non-printable control characters (except newline and carriage return).
    """
    return re.sub(r'[^\x20-\x7E\n\r]', '', text)

def replace_latex_symbols(text: str) -> str:
    """
    Replaces a few LaTeX-like symbols with plain text.
    """
    return (text
            .replace(r'\(', '')
            .replace(r'\)', '')
            .replace(r'\[', '')
            .replace(r'\]', '')
            .replace(r'\times', '*'))

def main():
    parser = argparse.ArgumentParser(description="Generate random arithmetic expressions in chat format as JSONL.")
    parser.add_argument(
        "-n", "--num_samples",
        type=int,
        default=1,
        help="Number of samples to generate."
    )
    parser.add_argument(
        "-d", "--difficulty",
        type=str,
        choices=["very easy", "easy", "pretty easy", "medium", "hard", "pretty hard", "very hard"],
        default="very easy",
        help="Set the difficulty level of the expression."
    )
    parser.add_argument(
        "--llm",
        type=str,
        default=None,
        help="Specify the name of the language model to use."
    )

    args = parser.parse_args()

    generator = ArithmeticExpressionGenerator()

    for _ in range(args.num_samples):
        # 1. Generate a random expression based on the chosen difficulty
        expression = generator.generate_random_expression(args.difficulty)
        print(expression)

        # 2. Compile the expression
        compiler = ArithmeticCompiler(expression)
        compiler.parse_expression()
        compiler.generate_instruction(args.llm)

        if not compiler.instruction:
            # If instruction generation fails, you may want to skip or print an error
            print("Failed to generate instruction.")
            continue

        # 3. Retrieve the emitted output in “chat” format
        #    The compiler’s `emit_chat()` method returns JSON (dict) serialised as a string (or you can serialise it here)
        chat_output = compiler.instruction.emit_chat()

        # Optionally strip control characters / replace LaTeX if needed
        chat_output = strip_control_characters(replace_latex_symbols(chat_output))

        # 4. Print each compiled chat sample as its own JSON line
        print(chat_output)

if __name__ == "__main__":
    main()
