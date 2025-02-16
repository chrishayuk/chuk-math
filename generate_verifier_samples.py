#!/usr/bin/env python3
import argparse
import json
import re
import yaml

# Local imports
from compiler.arithmetic_compiler import ArithmeticCompiler
from expression_generator.arithmetic_expression_generator import ArithmeticExpressionGenerator

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Generate JSONL with verifiers.")
    parser.add_argument(
        "-c", "--config",
        type=str,
        default="config.yaml",
        help="Path to a YAML config file specifying generation stages. "
             "Defaults to config.yaml"
    )
    return parser.parse_args()

def load_config(config_path: str) -> dict:
    """Load generation settings from YAML config."""
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def strip_control_characters(text: str) -> str:
    """Remove non-printable ASCII characters (other than \n and \r)."""
    return re.sub(r'[^\x20-\x7E\n\r]', '', text)

def replace_latex_symbols(text: str) -> str:
    """Replace some LaTeX-like tokens with plain text equivalents."""
    return (text
            .replace(r'\(', '')
            .replace(r'\)', '')
            .replace(r'\[', '')
            .replace(r'\]', '')
            .replace(r'\times', '*'))

def main():
    # Parse command-line arguments
    args = parse_args()

    # Load config from the specified YAML file (defaults to config.yaml)
    config = load_config(args.config)

    # If there's a top-level "verifier_url" in the YAML, use that; else default:
    default_verifier_url = config.get("verifier_url", "http://0.0.0.0:8000")

    # List of stages, each containing difficulty, count, optional LLM, template, etc.
    stages = config.get("stages", [])
    
    # Create the arithmetic expression generator
    generator = ArithmeticExpressionGenerator()

    # Loop through all the stages in the config
    for stage in stages:
        # Get the difficulty, defaulting to "very easy"
        difficulty = stage.get("difficulty", "very easy")

        # Get the count of samples
        count = stage.get("count", 1)

        # Get the LLM
        llm = stage.get("llm", "granite3.1-dense")

        # Get the template
        template_name = stage.get("template", "math_stepbystep_template.jinja")

        # Generate the specified number of samples
        for _ in range(count):
            # Generate an expression based on the difficulty
            expression = generator.generate_random_expression(difficulty)

            # Setup the arithmetic compiler
            compiler = ArithmeticCompiler(expression)
            compiler.parse_expression()
            compiler.generate_instruction(llm)

            # Check we got an instruction
            if not compiler.instruction:
                # If instruction generation failed, skip
                continue

            # Extract numeric result
            instruction_dict = compiler.instruction.emit_instruction()
            numeric_answer_str = instruction_dict.get("result", None)

            # We'll just store numeric_answer as the raw string (or None)
            numeric_answer = numeric_answer_str

            # Generate the chat prompt using the given template
            chat_output_str = compiler.instruction.emit_chat(template_name)

            # Clean up any control characters or LaTeX
            chat_output_str = strip_control_characters(
                replace_latex_symbols(chat_output_str)
            )

            # Extract user prompt from the chat JSON
            try:
                chat_output = json.loads(chat_output_str)
                user_message = next(
                    msg["content"] for msg in chat_output["messages"]
                    if msg["role"] == "user"
                )
            except (KeyError, StopIteration, json.JSONDecodeError):
                # If we can't parse the user message, skip
                continue

            # Build the verifiers list
            verifiers = [
                {
                    "name": "reasoning_format_with_verifier_answer",
                    "url": default_verifier_url
                }
            ]

            # If we have a numeric answer, add the "verifier_answer"
            if numeric_answer is not None:
                verifiers.append({
                    "name": "verifier_answer",
                    "url": default_verifier_url,
                    "args": {
                        "gold_solution": str(numeric_answer)
                    }
                })

            # Construct the JSONL entry
            jsonl_entry = {
                "prompt": user_message,
                "min_reward": 1.0,
                "verifiers": verifiers
            }

            # Output as a JSON line
            print(json.dumps(jsonl_entry))

if __name__ == "__main__":
    main()
