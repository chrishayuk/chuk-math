import json
import random
from decimal import Decimal, InvalidOperation, getcontext
from instructions.instruction_emitter import InstructionEmitter
from sympy import sympify, SympifyError

class InfixExpressionCalculatorInstruction(InstructionEmitter):
    def __init__(self, ast: dict, tokens: list = None):

        # check if we're parsing an ast or tokens
        if isinstance(ast, str):
            # we got an ast, load it
            ast = json.loads(ast)

        # call the parent constructor
        super().__init__(ast, tokens or [])

        # set the tokens
        self.tokens = tokens or []


    def get_random_instruction(self) -> str:
        # get the instruction templates
        templates = [
            lambda: f"Calculate the result of the expression: {self.expression}.",
            lambda: f"Solve the following expression: {self.expression}.",
            lambda: f"Evaluate the expression: {self.expression}.",
            lambda: f"Find the result of {self.expression}.",
            lambda: f"What is the value of {self.expression}?"
        ]

        # randomly pick a template
        return random.choice(templates)()

    def safe_eval(self, expression: str) -> Decimal:
        try:
            # evaluate expression
            sympy_expr = sympify(expression)

            # check for an error
            if sympy_expr is None:
                raise ValueError("Invalid expression resulting in None")
            
            # get the result
            result = sympy_expr.evalf()

            # return the value
            getcontext().prec = 64
            decimal_result = Decimal(str(result))
            return decimal_result.quantize(Decimal('1.0000')).normalize()
        except (SympifyError, InvalidOperation, ValueError) as error:
            # error
            raise ValueError(f"Invalid expression or calculation error: {error}")

    def generate_explanation(self):
        return "This explanation details the steps taken to evaluate the expression."
