import random
from decimal import Decimal, InvalidOperation, getcontext
from math import isfinite
from instructions.base_instruction import BaseInstruction
from lexer.arithmetic_expression import ArithmeticExpression
from sympy import sympify, SympifyError

class InfixExpressionCalculatorInstruction(BaseInstruction):
    def __init__(self, expression: str, original_expression: str):
        super().__init__(expression, original_expression)
        self.expression = original_expression

    def create_instruction(self) -> dict:
        # Generate the explanation (assuming similar logic is implemented)
        explanation = self.generate_explanation()  # Placeholder for actual explanation generation logic
        
        # calculate the results
        result = self.safe_eval(self.convert_tokens_to_eval_format(self.tokens))

        # return the instruction
        return {
            "instruction": self.get_random_instruction(),
            "expression": self.expression,
            "tokens": self.simplify_tokens(self.tokens),
            "result": str(result),
            "explanation": explanation
        }

    def get_random_instruction(self) -> str:
        templates = [
            lambda: f"Perform the following calculation for the arithmetic expression: {self.expression}",
            lambda: f"{self.expression}",
            lambda: f"Solve the expression: {self.expression}",
            lambda: f"{self.expression}: what's the answer?",
            lambda: f"Calculate {self.expression}.",
            lambda: f"What's {self.expression}?",
            lambda: f"Figure out the answer to {self.expression}",
            lambda: f"What is {self.expression} equal to?",
            lambda: f"Work out what {self.expression} is?",
            lambda: f"Work out {self.expression} and display the answer",
            lambda: f"Solve {self.expression}.",
            lambda: f"Tell me what {self.expression} is",
            lambda: f"Resolve {self.expression} and note the result.",
            lambda: f"Evaluate: {self.expression}.",
            lambda: f"Solve the arithmetic expression {self.expression}.",
            lambda: f"Calculate {self.expression} and show the result",
            lambda: f"What does the expression {self.expression} equal?",
            lambda: f"Find the value of this arithmetic challenge: {self.expression}.",
            lambda: f"Determine the outcome of the expression {self.expression}",
            lambda: f"For the arithmetic problem {self.expression}, what's the answer?",
            lambda: f"Work out the expression {self.expression}.",
            lambda: f"What result does {self.expression} yield?",
            lambda: f"Evaluate this: {self.expression} and return the result"
        ]

        return random.choice(templates)()

    def convert_tokens_to_eval_format(self, tokens: list) -> str:
        return ' '.join(str(token['value']) for token in tokens)

    def safe_eval(self, expression: str) -> Decimal:
        try:
            # Parse and evaluate the expression using sympy
            sympy_expr = sympify(expression)
            result = sympy_expr.evalf()  # Get the floating-point approximation as a sympy Float

            # Set the precision and rounding context for Decimal
            getcontext().prec = 64

            # Convert the sympy Float result to a string and then to a Decimal
            decimal_result = Decimal(str(result))

            # Normalize the result to remove trailing zeros and round to 4 decimal places
            decimal_result = decimal_result.quantize(Decimal('1.0000')).normalize()

            return decimal_result
        except (SympifyError, InvalidOperation, ValueError) as error:
            print(f"Error in calculation: {error}")
            raise ValueError(f"Invalid expression or calculation error: {error}")

    def generate_explanation(self):
        # Placeholder for the explanation generation logic
        return "Explanation of the steps taken in solving the expression."
