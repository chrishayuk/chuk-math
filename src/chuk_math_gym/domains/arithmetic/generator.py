"""
Arithmetic domain generator.

Wraps the existing ArithmeticExpressionGenerator to produce
Problem and Trace objects in the new schema format.
"""

import random
from decimal import getcontext
from typing import Optional, Tuple

import sympy

from chuk_math_gym.expression_generator.arithmetic_expression_generator import (
    ArithmeticExpressionGenerator as LegacyGenerator,
)
from chuk_math_gym.schemas.problem import (
    AnswerType,
    DifficultyLevel,
    DomainType,
    Problem,
    ToolPolicy,
)
from chuk_math_gym.schemas.trace import Trace
from chuk_math_gym.trace.ast_trace import ASTTraceGenerator

# Set high precision for calculations
getcontext().prec = 64


# Difficulty configuration mapping
DIFFICULTY_CONFIG = {
    DifficultyLevel.VERY_EASY: {
        "max_depth": 1,
        "base_operands": 2,
        "allow_negative": False,
        "allow_decimals": False,
        "min_number": 1,
        "max_number": 100,
        "allow_division": False,
        "decimal_places": 0,
    },
    DifficultyLevel.EASY: {
        "max_depth": 1,
        "base_operands": 2,
        "allow_negative": False,
        "allow_decimals": False,
        "min_number": 1,
        "max_number": 1000,
        "allow_division": False,
        "decimal_places": 0,
    },
    DifficultyLevel.PRETTY_EASY: {
        "max_depth": 1,
        "base_operands": 3,
        "allow_negative": True,
        "allow_decimals": False,
        "min_number": -1000,
        "max_number": 1000,
        "allow_division": True,
        "decimal_places": 0,
    },
    DifficultyLevel.MEDIUM: {
        "max_depth": 2,
        "base_operands": 3,
        "allow_negative": True,
        "allow_decimals": False,
        "min_number": -10000,
        "max_number": 10000,
        "allow_division": True,
        "decimal_places": 0,
    },
    DifficultyLevel.HARD: {
        "max_depth": 2,
        "base_operands": 4,
        "allow_negative": True,
        "allow_decimals": True,
        "min_number": -100000,
        "max_number": 100000,
        "allow_division": True,
        "decimal_places": 3,
    },
    DifficultyLevel.PRETTY_HARD: {
        "max_depth": 3,
        "base_operands": 4,
        "allow_negative": True,
        "allow_decimals": True,
        "min_number": -500000,
        "max_number": 500000,
        "allow_division": True,
        "decimal_places": 4,
    },
    DifficultyLevel.VERY_HARD: {
        "max_depth": 3,
        "base_operands": 5,
        "allow_negative": True,
        "allow_decimals": True,
        "min_number": -1000000,
        "max_number": 1000000,
        "allow_division": True,
        "decimal_places": 4,
    },
}


# Question templates
QUESTION_TEMPLATES = [
    "What is {expression}?",
    "Calculate: {expression}",
    "Evaluate {expression}",
    "Find the value of {expression}",
    "Compute: {expression}",
    "Solve: {expression}",
]


class ArithmeticGenerator:
    """
    Generator for arithmetic problems.

    Produces Problem and Trace objects from random expressions.
    Supports deterministic seeding for reproducibility.
    """

    def __init__(self):
        """Initialize the generator."""
        self._rng = random.Random()
        self._trace_generator = ASTTraceGenerator()
        self._legacy_generator = LegacyGenerator()

    def generate(
        self,
        seed: Optional[int] = None,
        difficulty: DifficultyLevel = DifficultyLevel.MEDIUM,
        tool_policy: ToolPolicy = ToolPolicy.ALLOWED,
        _retry_count: int = 0,
    ) -> Tuple[Problem, Trace]:
        """
        Generate a problem and its solution trace.

        Args:
            seed: Random seed for reproducibility
            difficulty: Difficulty level
            tool_policy: Tool usage policy
            _retry_count: Internal counter to prevent infinite recursion

        Returns:
            Tuple of (Problem, Trace)

        Raises:
            RuntimeError: If maximum retries exceeded
        """
        MAX_RETRIES = 10

        # Set seed
        if seed is None:
            seed = random.randint(0, 2**31 - 1)
        self._rng.seed(seed)
        random.seed(seed)  # Also seed global random for legacy generator

        # Generate expression
        expression = self._generate_expression(difficulty)

        # Evaluate to get answer
        try:
            answer = self._evaluate_expression(expression)
        except Exception as e:
            # If evaluation fails, retry with limit
            if _retry_count >= MAX_RETRIES:
                raise RuntimeError(
                    f"Failed to generate valid expression after {MAX_RETRIES} attempts. "
                    f"Last error: {e}"
                )
            return self.generate(seed + 1, difficulty, tool_policy, _retry_count + 1)

        # Format answer
        config = DIFFICULTY_CONFIG[difficulty]
        if config["allow_decimals"]:
            answer_str = f"{answer:.{config['decimal_places']}f}"
            answer_type = AnswerType.NUMERIC
            tolerance = 10 ** (-config["decimal_places"])
        else:
            answer_str = str(int(round(answer)))
            answer_type = AnswerType.EXACT
            tolerance = None

        # Generate prompt
        template = self._rng.choice(QUESTION_TEMPLATES)
        prompt = template.format(expression=expression)

        # Count operations
        operation_count = sum(1 for c in expression if c in "+-*/")

        # Create Problem
        problem = Problem(
            id=Problem.generate_id(DomainType.ARITHMETIC, difficulty, seed),
            seed=seed,
            domain=DomainType.ARITHMETIC,
            difficulty=difficulty,
            prompt=prompt,
            expression=expression,
            answer_type=answer_type,
            gold_answer=answer_str,
            tolerance=tolerance,
            tool_policy=tool_policy,
            depth=config["max_depth"],
            operation_count=operation_count,
            numeric_range=(config["min_number"], config["max_number"]),
            has_decimals=bool(config["allow_decimals"]),
            has_negatives=bool(config["allow_negative"]),
            tags=["arithmetic", difficulty.value],
            common_mistakes=self._get_common_mistakes(expression),
        )

        # Generate trace using AST-based generator
        trace = self._trace_generator.generate_from_expression(expression, problem.id)

        return problem, trace

    def _generate_expression(self, difficulty: DifficultyLevel) -> str:
        """Generate a random expression for the given difficulty."""
        # Map enum to string for expression generator
        difficulty_str = difficulty.value.replace("_", " ")
        return str(self._legacy_generator.generate_random_expression(difficulty_str))

    def _simple_expression(self, config: dict) -> str:
        """Simple fallback expression generator."""
        operators = ["+", "-", "*"]
        if config["allow_division"]:
            operators.append("/")

        num_ops = config["base_operands"] - 1

        def rand_num():
            val = self._rng.randint(config["min_number"], config["max_number"])
            if not config["allow_negative"]:
                val = abs(val)
            return str(val)

        expr = rand_num()
        for _ in range(num_ops):
            op: str = self._rng.choice(operators)
            next_num = rand_num()
            # Avoid division by zero
            if op == "/" and next_num in ("0", "-0"):
                next_num = str(self._rng.randint(1, 10))
            expr = f"{expr} {op} {next_num}"

        return str(expr)

    def _evaluate_expression(self, expression: str) -> float:
        """
        Safely evaluate an arithmetic expression.

        Uses sympy for safe evaluation, with AST-based fallback.
        """
        try:
            result = sympy.sympify(expression).evalf()
            return float(result)
        except (ValueError, TypeError, AttributeError, sympy.SympifyError):
            # Fallback to safe AST-based evaluation for:
            # - Invalid expression syntax (ValueError, SympifyError)
            # - Type conversion issues (TypeError)
            # - Expression object access issues (AttributeError)
            return self._safe_ast_eval(expression)

    def _safe_ast_eval(self, expression: str) -> float:
        """
        Safely evaluate expression using Python's AST module.

        This is safer than eval() as it only allows numeric operations.
        """
        import ast
        import operator

        ops = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Pow: operator.pow,
            ast.USub: operator.neg,
            ast.UAdd: operator.pos,
        }

        def _eval(node):
            if isinstance(node, ast.Num):
                return node.n
            elif isinstance(node, ast.Constant):
                if isinstance(node.value, (int, float)):
                    return node.value
                raise ValueError(f"Invalid constant: {node.value}")
            elif isinstance(node, ast.BinOp):
                return ops[type(node.op)](_eval(node.left), _eval(node.right))
            elif isinstance(node, ast.UnaryOp):
                return ops[type(node.op)](_eval(node.operand))
            elif isinstance(node, ast.Expression):
                return _eval(node.body)
            else:
                raise ValueError(f"Unsupported: {type(node)}")

        tree = ast.parse(expression, mode="eval")
        return float(_eval(tree))

    def _get_common_mistakes(self, expression: str) -> list[str]:
        """Identify common mistakes for this expression type."""
        mistakes = []

        # Check for order of operations traps
        if "*" in expression or "/" in expression:
            if "+" in expression or "-" in expression:
                mistakes.append("order_of_operations")

        # Check for negative numbers
        if "-" in expression:
            mistakes.append("sign_error")

        # Check for division
        if "/" in expression:
            mistakes.append("division_error")

        return mistakes

    def generate_batch(
        self,
        count: int,
        difficulty: DifficultyLevel = DifficultyLevel.MEDIUM,
        start_seed: Optional[int] = None,
    ) -> list[Tuple[Problem, Trace]]:
        """
        Generate a batch of problems.

        Args:
            count: Number of problems to generate
            difficulty: Difficulty level
            start_seed: Starting seed (problems use sequential seeds)

        Returns:
            List of (Problem, Trace) tuples
        """
        if start_seed is None:
            start_seed = random.randint(0, 2**31 - 1)

        return [self.generate(seed=start_seed + i, difficulty=difficulty) for i in range(count)]
