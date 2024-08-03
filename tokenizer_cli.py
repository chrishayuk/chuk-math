import argparse
import json
from compiler.parser.arithmetic_expression import ArithmeticExpression

def main():
    # Setup argument parser
    parser = argparse.ArgumentParser(description="Tokenize an arithmetic expression and output as JSON.")
    parser.add_argument(
        "expression",
        type=str,
        help="The arithmetic expression to tokenize."
    )

    args = parser.parse_args()

    # Initialize the arithmetic expression parser
    arithmetic_expression = ArithmeticExpression(args.expression)

    try:
        # Tokenize the expression
        tokens = arithmetic_expression.tokenize()
        
        # Convert tokens to a JSON-serializable format
        token_list = [{"type": token.type, "value": token.value, "position": token.position} for token in tokens]
        
        # Output tokens as JSON
        print(json.dumps({"tokens": token_list}, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}))

if __name__ == "__main__":
    main()
