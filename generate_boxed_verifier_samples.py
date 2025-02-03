#!/usr/bin/env python3
import argparse
import json
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
    parser = argparse.ArgumentParser(description="Generate JSONL with the user question from emit_chat, plus verifiers.")
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
        help="Specify the language model name if needed."
    )
    args = parser.parse_args()

    generator = ArithmeticExpressionGenerator()

    for _ in range(args.num_samples):
        # 1. Generate a random expression (e.g. "80 + 91")
        expression = generator.generate_random_expression(args.difficulty)

        # 2. Compile the expression
        compiler = ArithmeticCompiler(expression)
        compiler.parse_expression()
        compiler.generate_instruction(args.llm)
        if not compiler.instruction:
            print("Failed to generate instruction.")
            continue

        # 3. Retrieve a Python dict from the instruction emitter
        #    e.g. {
        #       "instruction": "What is 389 + 646?",
        #       "expression": "389 + 646",
        #       "result": "1035",
        #       ...
        #    }
        instruction_dict = compiler.instruction.emit_instruction()

        # 4. Retrieve the numeric answer (string) from the instruction
        numeric_answer_str = instruction_dict.get("result", None)
        # Try converting to an integer (or float) if it’s truly numeric.
        # Some instructions might return a string like "No solution" or an empty string.
        try:
            numeric_answer = int(float(numeric_answer_str))  # handles "1035", "1035.0"
        except (ValueError, TypeError):
            numeric_answer = None

        # 5. Retrieve JSON from emit_chat() for the user question
        step_by_step_template_name = "math_stepbystep_template.jinja"
        chat_output_str = compiler.instruction.emit_chat(step_by_step_template_name)

        # Clean up the raw JSON string
        chat_output_str = strip_control_characters(replace_latex_symbols(chat_output_str))

        # 6. Parse JSON to find the user's question
        try:
            chat_output = json.loads(chat_output_str)
            # Find the first user message (the prompt)
            user_message = next(
                msg["content"] for msg in chat_output["messages"] if msg["role"] == "user"
            )
        except (KeyError, StopIteration, json.JSONDecodeError):
            print("Could not parse user message from emit_chat output.")
            continue

        # 7. Build the verifiers list
        verifiers = [
            {
                "name": "reasoning_format",
                "url": "http://0.0.0.0:8000"
            }
        ]
        # If we have a numeric answer, add the "boxed_answer" verifier with gold_solution
        if numeric_answer is not None:
            verifiers.append({
                "name": "boxed_answer",
                "url": "http://0.0.0.0:8000",
                "args": {
                    "gold_solution": f"\\(\\boxed{{{numeric_answer}}}\\)"
                }
            })

        # 8. Construct the final JSON line
        jsonl_entry = {
            "prompt": user_message,
            "verifiers": verifiers
        }

        # 9. Print as a single JSON line
        print(json.dumps(jsonl_entry))

if __name__ == "__main__":
    main()
