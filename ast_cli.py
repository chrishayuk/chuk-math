import argparse
import json
from compiler.parser.arithmetic_expression import ArithmeticExpression

def main():
    # Setup argument parser
    parser = argparse.ArgumentParser(description="Generate an AST from an arithmetic expression and output as JSON.")

    # add the argument
    parser.add_argument(
        "expression",
        type=str,
        help="The arithmetic expression to parse."
    )

    # pass the args
    args = parser.parse_args()

    # Initialize the arithmetic expression parser
    arithmetic_expression = ArithmeticExpression(args.expression)

    try:
        # Parse the expression into an AST
        ast = arithmetic_expression.parse()

        # Convert AST to dictionary format
        ast_dict = arithmetic_expression.ast_to_dict(ast)

        # Output the AST as JSON
        print(json.dumps({"ast": ast_dict}, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}))

if __name__ == "__main__":
    main()
