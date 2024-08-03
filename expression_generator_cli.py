import argparse
from expression_generator.utilities.random_number_generator import generate_random_number
from expression_generator.utilities.random_operator_generator import generate_random_operator
from expression_generator.arithmetic_expression_generator import ArithmeticExpressionGenerator

def main():
    # Setup argument parser
    parser = argparse.ArgumentParser(description="Generate random arithmetic expressions.")

    # difficulty
    parser.add_argument(
        "-d", "--difficulty",
        type=str,
        choices=["very easy", "easy", "pretty easy", "medium", "hard", "pretty hard", "very hard"],
        default="very easy",
        help="Set the difficulty level of the expression."
    )

    # parse
    args = parser.parse_args()

    # Initialize the generator
    generator = ArithmeticExpressionGenerator()

    # Generate the expression
    expression = generator.generate_random_expression(args.difficulty)

    # Print the generated expression
    print(f"Generated Expression: {expression}")

if __name__ == "__main__":
    main()
