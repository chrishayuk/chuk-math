import json
import random
from decimal import Decimal, InvalidOperation, getcontext
from instructions.instruction_emitter import InstructionEmitter
from sympy import sympify, SympifyError

class InfixExpressionCalculatorInstruction(InstructionEmitter):
    def __init__(self, ast: dict, tokens: list = None):
        # Ensure ast is a dictionary; if not, attempt to load it as JSON
        if isinstance(ast, str):
            ast = json.loads(ast)
        super().__init__(ast, tokens or [])
        self.tokens = tokens or []  # Store tokens
        print(f"Initialized with tokens: {self.tokens}")  # Debug

    def emit_instruction(self, mode: str = "ast", minimal_parentheses: bool = False) -> dict:
        if mode == "tokens":
            return self.emit_instruction_tokens()
        return self.emit_instruction_ast(minimal_parentheses)

    def emit_instruction_ast(self, minimal_parentheses: bool = False) -> dict:
        self.expression = self.extract_expression_from_ast(self.ast, minimal_parentheses)
        explanation = self.generate_explanation()
        try:
            result = self.safe_eval(self.expression)
            result_str = str(result)  # Convert Decimal to string for JSON serialization
        except ValueError as error:
            result_str = str(error)

        return {
            "instruction": self.get_random_instruction(),
            "expression": self.expression,
            "tokens": self.simplify_tokens(self.tokens),
            "result": result_str,
            "explanation": explanation
        }

    def emit_instruction_tokens(self) -> dict:
        self.expression = self.extract_expression_from_tokens(self.tokens)
        simplified_tokens = self.simplify_tokens(self.tokens)
        print(f"Simplified tokens: {simplified_tokens}")  # Debug
        return {
            "instruction": f"Tokens representation of the expression: {self.expression}",
            "tokens": simplified_tokens,
            "result": "Tokenized form does not include evaluation",
            "explanation": "Tokens represent the lexical elements of the expression."
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

    def safe_eval(self, expression: str) -> Decimal:
        try:
            print(f"Evaluating expression: {expression}")  # Debug: show the expression to be evaluated
            sympy_expr = sympify(expression)
            if sympy_expr is None:
                raise ValueError("Invalid expression resulting in None")
            result = sympy_expr.evalf()
            getcontext().prec = 64
            decimal_result = Decimal(str(result))
            return decimal_result.quantize(Decimal('1.0000')).normalize()
        except (SympifyError, InvalidOperation, ValueError) as error:
            raise ValueError(f"Invalid expression or calculation error: {error}")

    def generate_explanation(self):
        return "Explanation of the steps taken in solving the expression."
