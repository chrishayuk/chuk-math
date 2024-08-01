import json
import random
from decimal import Decimal, InvalidOperation, getcontext
from instructions.instruction_emitter import InstructionEmitter
from sympy import sympify, SympifyError

class InfixExpressionCalculatorInstruction(InstructionEmitter):
    def __init__(self, ast: dict):
        # Ensure ast is a dictionary; if not, attempt to load it as JSON
        if isinstance(ast, str):
            ast = json.loads(ast)
        
        # call the parent constructor
        super().__init__(ast)

        # set the ast
        self.ast = ast

        # get the expression
        self.expression = ast.get('expression', '')  # Safely get 'expression' from ast

    def emit_instruction(self) -> dict:
        # Generate the explanation
        explanation = self.generate_explanation()
        
        # Calculate the result
        result = self.safe_eval(self.convert_tokens_to_eval_format(self.tokens))

        # Return the instruction
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

        # randomly choose a template
        return random.choice(templates)()

    def convert_tokens_to_eval_format(self, tokens: list) -> str:
        # convert tokens for eval
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
