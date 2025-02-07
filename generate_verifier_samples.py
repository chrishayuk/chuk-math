#!/usr/bin/env python3
import argparse
import json
import re

from compiler.arithmetic_compiler import ArithmeticCompiler
from expression_generator.arithmetic_expression_generator import ArithmeticExpressionGenerator

def strip_control_characters(text: str) -> str:
    return re.sub(r'[^\x20-\x7E\n\r]', '', text)

def replace_latex_symbols(text: str) -> str:
    return (text
            .replace(r'\(', '')
            .replace(r'\)', '')
            .replace(r'\[', '')
            .replace(r'\]', '')
            .replace(r'\times', '*'))

def main():
    parser = argparse.ArgumentParser(description="Generate JSONL with verifiers (reasoning_format, answer_satisfaction, verifier_answer).")
    parser.add_argument("-n", "--num_samples", type=int, default=1,
                        help="Number of samples to generate.")
    parser.add_argument("-d", "--difficulty", type=str,
                        choices=["very easy", "easy", "pretty easy", "medium", "hard", "pretty hard", "very hard"],
                        default="very easy", help="Difficulty level of the expression.")
    parser.add_argument("--llm", type=str, default=None, help="Specify the language model name if needed.")
    args = parser.parse_args()

    generator = ArithmeticExpressionGenerator()

    for _ in range(args.num_samples):
        expression = generator.generate_random_expression(args.difficulty)

        compiler = ArithmeticCompiler(expression)
        compiler.parse_expression()
        compiler.generate_instruction(args.llm)
        if not compiler.instruction:
            print("Failed to generate instruction.")
            continue

        # get the instruction dict => to extract result
        instruction_dict = compiler.instruction.emit_instruction()
        numeric_answer_str = instruction_dict.get("result", None)
        try:
            numeric_answer = int(float(numeric_answer_str))
        except (ValueError, TypeError):
            numeric_answer = None

        # get chat JSON for user prompt
        step_by_step_template_name = "math_stepbystep_template.jinja"
        chat_output_str = compiler.instruction.emit_chat(step_by_step_template_name)
        chat_output_str = strip_control_characters(replace_latex_symbols(chat_output_str))

        try:
            chat_output = json.loads(chat_output_str)
            user_message = next(
                msg["content"] for msg in chat_output["messages"] if msg["role"] == "user"
            )
        except (KeyError, StopIteration, json.JSONDecodeError):
            print("Could not parse user message.")
            continue

        # Always add 'reasoning_format' verifier
        verifiers = [
            {
                "name": "reasoning_format",
                "url": "http://0.0.0.0:8000"
            }
        ]

        # If we have a numeric_answer, add 'answer_satisfaction' + 'verifier_answer'
        if numeric_answer is not None:
            verifiers.append({
                "name": "answer_satisfaction",
                "url": "http://0.0.0.0:8000",
                "args": {
                    "question": user_message,
                    "gold_answer": str(numeric_answer)
                }
            })
            verifiers.append({
                "name": "verifier_answer",
                "url": "http://0.0.0.0:8000",
                "args": {
                    "gold_solution": str(numeric_answer)
                }
            })

        jsonl_entry = {
            "prompt": user_message,
            "verifiers": verifiers
        }

        print(json.dumps(jsonl_entry))

if __name__ == "__main__":
    main()
