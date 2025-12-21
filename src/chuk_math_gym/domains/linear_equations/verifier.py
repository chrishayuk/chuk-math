"""
Linear equations domain verifier.

Handles verification of equation solutions including:
- Numeric solutions
- Fractional solutions
- Substitution checking
"""

import ast
import operator
import re
from fractions import Fraction
from typing import Any, Callable, Dict, Optional, Type

from chuk_math_gym.schemas.problem import Problem
from chuk_math_gym.schemas.trace import Trace
from chuk_math_gym.schemas.verification import (
    VerificationResult,
    ErrorType,
)
from chuk_math_gym.verifiers.base import Verifier


class LinearEquationsVerifier(Verifier):
    """
    Verifier for linear equation solutions.

    Supports:
    - Numeric solutions (x = 5)
    - Fractional solutions (x = 3/4)
    - Decimal approximations
    - Substitution verification
    """

    def __init__(self, tolerance: float = 1e-9):
        """
        Initialize the linear equations verifier.

        Args:
            tolerance: Tolerance for numeric comparisons
        """
        self.tolerance = tolerance

    def verify_final(
        self,
        problem: Problem,
        candidate: str,
    ) -> VerificationResult:
        """
        Verify a solution to a linear equation.

        Parses various formats:
        - "x = 5" or just "5"
        - "3/4" or "x = 3/4"
        - "0.75"
        """
        # Parse candidate
        candidate_val = self._parse_solution(candidate)

        if candidate_val is None:
            return VerificationResult(
                correct=False,
                score=0.0,
                error_type=ErrorType.INVALID_FORMAT,
                error_message=f"Could not parse '{candidate}' as a number",
            )

        # Parse gold answer
        gold_val = self._parse_solution(problem.gold_answer)

        if gold_val is None:
            return VerificationResult(
                correct=False,
                score=0.0,
                error_type=ErrorType.INVALID_FORMAT,
                error_message=f"Invalid gold answer: {problem.gold_answer}",
            )

        # Check if values match
        tolerance = problem.tolerance or self.tolerance
        diff = abs(float(gold_val) - float(candidate_val))

        if diff <= tolerance:
            return VerificationResult(
                correct=True,
                score=1.0,
                error_type=ErrorType.NONE,
                expected=float(gold_val),
                actual=float(candidate_val),
                tolerance_used=tolerance,
            )

        # Classify error
        error_type = self._classify_error(gold_val, candidate_val)

        return VerificationResult(
            correct=False,
            score=0.0,
            error_type=error_type,
            error_message=self._get_error_message(error_type, gold_val, candidate_val),
            expected=float(gold_val),
            actual=float(candidate_val),
            tolerance_used=tolerance,
        )

    def verify_trace(
        self,
        problem: Problem,
        trace: Trace,
    ) -> VerificationResult:
        """Verify a complete solution trace."""
        if not trace.steps:
            return VerificationResult(
                correct=False,
                score=0.0,
                error_type=ErrorType.INCOMPLETE,
                error_message="Empty trace",
                steps_correct=0,
                steps_total=0,
            )

        steps_correct = 0
        first_error_step = None

        for i, step in enumerate(trace.steps):
            expected = trace.placeholder_map.get(step.output)
            if expected is None:
                first_error_step = i
                break

            if not step.verify_output(expected, self.tolerance):
                first_error_step = i
                break

            steps_correct += 1

        # Verify final answer
        gold_val = self._parse_solution(problem.gold_answer)
        if gold_val is None:
            return VerificationResult(
                correct=False,
                score=0.0,
                error_type=ErrorType.INVALID_FORMAT,
            )

        final_correct = abs(trace.final_value - float(gold_val)) < self.tolerance

        if first_error_step is None and final_correct:
            return VerificationResult(
                correct=True,
                score=1.0,
                error_type=ErrorType.NONE,
                steps_correct=steps_correct,
                steps_total=trace.total_steps,
            )

        partial_credit = self.compute_partial_credit(trace, first_error_step)

        return VerificationResult(
            correct=False,
            score=partial_credit,
            partial_credit=partial_credit,
            error_type=ErrorType.WRONG_ANSWER,
            steps_correct=steps_correct,
            steps_total=trace.total_steps,
            first_error_step=first_error_step,
        )

    def verify_step(
        self,
        problem: Problem,
        trace: Trace,
        step_index: int,
        candidate_value: float,
    ) -> VerificationResult:
        """Verify a single step."""
        if step_index < 0 or step_index >= len(trace.steps):
            return VerificationResult(
                correct=False,
                score=0.0,
                error_type=ErrorType.INVALID_FORMAT,
                error_message=f"Step index {step_index} out of range",
            )

        step = trace.steps[step_index]
        expected = step.output_value

        if abs(expected - candidate_value) <= self.tolerance:
            return VerificationResult(
                correct=True,
                score=1.0,
                error_type=ErrorType.NONE,
                expected=expected,
                actual=candidate_value,
            )

        return VerificationResult(
            correct=False,
            score=0.0,
            error_type=ErrorType.WRONG_ANSWER,
            expected=expected,
            actual=candidate_value,
        )

    def verify_by_substitution(
        self,
        equation: str,
        variable: str,
        candidate: float,
    ) -> VerificationResult:
        """
        Verify a solution by substituting back into the equation.

        This is an additional verification method that checks if the
        candidate value satisfies the original equation.
        """
        try:
            # Parse equation: left = right
            if "=" not in equation:
                return VerificationResult(
                    correct=False,
                    score=0.0,
                    error_type=ErrorType.INVALID_FORMAT,
                    error_message="Equation must contain '='",
                )

            left, right = equation.split("=", 1)

            # Substitute variable
            left_val = self._evaluate_side(left.strip(), variable, candidate)
            right_val = self._evaluate_side(right.strip(), variable, candidate)

            if left_val is None or right_val is None:
                return VerificationResult(
                    correct=False,
                    score=0.0,
                    error_type=ErrorType.INVALID_FORMAT,
                    error_message="Could not evaluate equation",
                )

            if abs(left_val - right_val) < self.tolerance:
                return VerificationResult(
                    correct=True,
                    score=1.0,
                    error_type=ErrorType.NONE,
                )

            return VerificationResult(
                correct=False,
                score=0.0,
                error_type=ErrorType.WRONG_ANSWER,
                error_message=f"Substitution gives {left_val} ≠ {right_val}",
            )

        except Exception as e:
            return VerificationResult(
                correct=False,
                score=0.0,
                error_type=ErrorType.INVALID_FORMAT,
                error_message=str(e),
            )

    def _parse_solution(self, answer: str) -> Optional[Fraction]:
        """Parse a solution value."""
        if not answer:
            return None

        answer = answer.strip()

        # Remove "x = " prefix if present
        answer = re.sub(r"^[a-zA-Z]\s*=\s*", "", answer)
        answer = answer.strip()

        try:
            # Try fraction: "3/4"
            if "/" in answer:
                parts = answer.split("/")
                if len(parts) == 2:
                    num = int(parts[0].strip())
                    den = int(parts[1].strip())
                    if den != 0:
                        return Fraction(num, den)

            # Try integer
            if re.match(r"^-?\d+$", answer):
                return Fraction(int(answer), 1)

            # Try decimal
            return Fraction(float(answer)).limit_denominator(10000)

        except (ValueError, ZeroDivisionError):
            return None

    def _classify_error(
        self,
        expected: Fraction,
        actual: Fraction,
    ) -> ErrorType:
        """Classify the type of error."""
        # Sign error
        if abs(expected) == abs(actual) and expected != actual:
            return ErrorType.SIGN_ERROR

        # Close value
        if abs(float(expected) - float(actual)) < 1.0:
            return ErrorType.ROUNDING_ERROR

        # Coefficient error (off by a factor)
        if expected != 0 and actual != 0:
            ratio = float(expected) / float(actual)
            if abs(ratio - round(ratio)) < 0.01:
                return ErrorType.COEFFICIENT_ERROR

        return ErrorType.WRONG_ANSWER

    def _get_error_message(
        self,
        error_type: ErrorType,
        expected: Fraction,
        actual: Fraction,
    ) -> str:
        """Generate error message."""
        exp_str = str(float(expected)) if expected.denominator != 1 else str(expected.numerator)
        act_str = str(float(actual)) if actual.denominator != 1 else str(actual.numerator)

        messages = {
            ErrorType.SIGN_ERROR: f"Sign error: expected {exp_str}, got {act_str}",
            ErrorType.ROUNDING_ERROR: f"Close but not exact: expected {exp_str}, got {act_str}",
            ErrorType.COEFFICIENT_ERROR: f"Coefficient error: expected {exp_str}, got {act_str}",
            ErrorType.WRONG_ANSWER: f"Incorrect: expected {exp_str}, got {act_str}",
        }

        return messages.get(error_type, f"Expected {exp_str}, got {act_str}")

    def _evaluate_side(
        self,
        expression: str,
        variable: str,
        value: float,
    ) -> Optional[float]:
        """Evaluate one side of an equation with variable substituted."""
        try:
            # Replace variable with value
            # Handle cases like "2x" -> "2*value"
            # Use re.escape() to safely handle special regex characters in variable names
            expr = re.sub(
                rf"(\d*)({re.escape(variable)})",
                lambda m: f"({m.group(1) or '1'}*{value})",
                expression,
            )

            # Use safe AST-based evaluation instead of eval()
            return self._safe_eval(expr)

        except (ValueError, SyntaxError, TypeError, ZeroDivisionError):
            return None

    def _safe_eval(self, expression: str) -> Optional[float]:
        """
        Safely evaluate a mathematical expression using Python's AST.

        Only allows basic arithmetic operations (+, -, *, /).
        """
        # Allowed operators - typed as Any to handle both binary and unary operators
        ops: Dict[Type[Any], Callable[..., float]] = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.USub: operator.neg,
            ast.UAdd: operator.pos,
        }

        def _eval_node(node: ast.AST) -> float:
            if isinstance(node, ast.Expression):
                return _eval_node(node.body)
            elif isinstance(node, ast.Constant):
                if isinstance(node.value, (int, float)):
                    return float(node.value)
                raise ValueError(f"Unsupported constant type: {type(node.value)}")
            elif isinstance(node, ast.BinOp):
                if type(node.op) not in ops:
                    raise ValueError(f"Unsupported operator: {type(node.op)}")
                left = _eval_node(node.left)
                right = _eval_node(node.right)
                return float(ops[type(node.op)](left, right))
            elif isinstance(node, ast.UnaryOp):
                if type(node.op) not in ops:
                    raise ValueError(f"Unsupported unary operator: {type(node.op)}")
                operand = _eval_node(node.operand)
                return float(ops[type(node.op)](operand))
            else:
                raise ValueError(f"Unsupported AST node: {type(node)}")

        try:
            tree = ast.parse(expression, mode="eval")
            return _eval_node(tree)
        except (SyntaxError, ValueError, TypeError, ZeroDivisionError):
            return None
