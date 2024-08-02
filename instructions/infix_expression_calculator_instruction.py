import json
import random
from decimal import Decimal, InvalidOperation, getcontext
from instructions.instruction_emitter import InstructionEmitter
from sympy import sympify, SympifyError

class InfixExpressionCalculatorInstruction(InstructionEmitter):
    def __init__(self, ast: dict, tokens: list = None):
        # Check if we're parsing an ast or tokens
        if isinstance(ast, str):
            ast = json.loads(ast)

        # Call the parent constructor
        super().__init__(ast, tokens or [])

        # Set the tokens
        self.tokens = tokens or []

    def get_random_instruction(self) -> str:
        # Get the instruction templates
        templates = [
            lambda: f"Calculate the result of the expression: {self.expression}.",
            lambda: f"Solve the following expression: {self.expression}.",
            lambda: f"Evaluate the expression: {self.expression}.",
            lambda: f"Find the result of {self.expression}.",
            lambda: f"What is the value of {self.expression}?"
        ]

        # Randomly pick a template
        return random.choice(templates)()

    def safe_eval(self, expression: str) -> Decimal:
        try:
            # Evaluate expression
            sympy_expr = sympify(expression)

            # Check for an error
            if sympy_expr is None:
                raise ValueError("Invalid expression resulting in None")
            
            # Get the result
            result = sympy_expr.evalf()

            # Return the value
            getcontext().prec = 64
            decimal_result = Decimal(str(result))
            return decimal_result.quantize(Decimal('1.0000')).normalize()
        except (SympifyError, InvalidOperation, ValueError) as error:
            raise ValueError(f"Invalid expression or calculation error: {error}")

    def generate_explanation(self):
        return "This explanation details the steps taken to evaluate the expression."
