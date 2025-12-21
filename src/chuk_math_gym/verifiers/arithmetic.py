"""
Arithmetic domain verifier.

Handles verification of arithmetic expressions including:
- Integer and decimal comparisons
- Tolerance-based approximate matching
- Error classification (sign errors, order of operations, etc.)
- Step-by-step trace verification
"""

import re
from typing import Optional

from chuk_math_gym.schemas.problem import Problem, AnswerType
from chuk_math_gym.schemas.trace import Trace
from chuk_math_gym.schemas.verification import (
    VerificationResult,
    ErrorType,
    ToolCallGrade,
)
from chuk_math_gym.verifiers.base import Verifier


class ArithmeticVerifier(Verifier):
    """
    Verifier for arithmetic domain problems.

    Supports:
    - Exact integer matching
    - Numeric matching with configurable tolerance
    - Error classification based on common arithmetic mistakes
    - Trace verification with partial credit
    """

    def __init__(self, default_tolerance: float = 1e-9):
        """
        Initialize the arithmetic verifier.

        Args:
            default_tolerance: Default tolerance for numeric comparisons
        """
        self.default_tolerance = default_tolerance

    def verify_final(
        self,
        problem: Problem,
        candidate: str,
    ) -> VerificationResult:
        """
        Verify a final answer against the gold answer.

        Handles various answer formats:
        - Plain numbers: "42", "-3.14", "1.5e-3"
        - Boxed LaTeX: "\\boxed{42}"
        - With units or text: "42 apples" -> extracts "42"
        """
        # Extract numeric value from candidate
        candidate_val = self._parse_answer(candidate)

        if candidate_val is None:
            return VerificationResult(
                correct=False,
                score=0.0,
                error_type=ErrorType.INVALID_FORMAT,
                error_message=f"Could not parse '{candidate}' as a number",
            )

        # Get expected value
        expected_val = self._parse_answer(problem.gold_answer)

        if expected_val is None:
            # This shouldn't happen with valid problems
            return VerificationResult(
                correct=False,
                score=0.0,
                error_type=ErrorType.INVALID_FORMAT,
                error_message=f"Invalid gold answer: {problem.gold_answer}",
            )

        # Determine tolerance
        if problem.answer_type == AnswerType.EXACT:
            tolerance = 0.0
        else:
            tolerance = problem.tolerance or self.default_tolerance

        # Check correctness
        diff = abs(expected_val - candidate_val)
        correct = diff <= tolerance

        if correct:
            return VerificationResult(
                correct=True,
                score=1.0,
                error_type=ErrorType.NONE,
                expected=expected_val,
                actual=candidate_val,
                tolerance_used=tolerance,
            )

        # Classify the error
        error_type = self._classify_error(expected_val, candidate_val)

        return VerificationResult(
            correct=False,
            score=0.0,
            error_type=error_type,
            error_message=self._get_error_message(error_type, expected_val, candidate_val),
            expected=expected_val,
            actual=candidate_val,
            tolerance_used=tolerance,
        )

    def verify_trace(
        self,
        problem: Problem,
        trace: Trace,
    ) -> VerificationResult:
        """
        Verify a complete solution trace step by step.

        Provides partial credit for correct intermediate steps.
        """
        if not trace.steps:
            return VerificationResult(
                correct=False,
                score=0.0,
                error_type=ErrorType.INCOMPLETE,
                error_message="Empty trace",
                steps_correct=0,
                steps_total=0,
            )

        first_error_step = None
        steps_correct = 0

        for i, step in enumerate(trace.steps):
            # Verify this step's output matches the placeholder map
            expected_value = trace.placeholder_map.get(step.output)

            if expected_value is None:
                first_error_step = i
                break

            if not step.verify_output(expected_value, self.default_tolerance):
                first_error_step = i
                break

            steps_correct += 1

        # Check final answer
        try:
            gold_value = float(problem.gold_answer)
        except (ValueError, TypeError):
            # Gold answer is not a simple float (e.g., "1/2")
            # Try to parse as fraction
            try:
                from fractions import Fraction

                gold_value = float(Fraction(problem.gold_answer))
            except (ValueError, TypeError):
                # Cannot parse gold answer - return error
                return VerificationResult(
                    correct=False,
                    score=0.0,
                    error_type=ErrorType.INVALID_FORMAT,
                    error_message=f"Cannot parse gold answer: {problem.gold_answer}",
                    steps_correct=steps_correct,
                    steps_total=trace.total_steps,
                )

        final_correct = trace.verify_final(gold_value, self.default_tolerance)

        if first_error_step is None and final_correct:
            return VerificationResult(
                correct=True,
                score=1.0,
                error_type=ErrorType.NONE,
                steps_correct=steps_correct,
                steps_total=trace.total_steps,
                expected=gold_value,
                actual=trace.final_value,
            )

        # Compute partial credit
        partial_credit = self.compute_partial_credit(trace, first_error_step)

        return VerificationResult(
            correct=False,
            score=partial_credit,
            partial_credit=partial_credit,
            error_type=ErrorType.WRONG_ANSWER,
            error_message=f"Error at step {first_error_step}"
            if first_error_step
            else "Final answer incorrect",
            steps_correct=steps_correct,
            steps_total=trace.total_steps,
            first_error_step=first_error_step,
            expected=float(problem.gold_answer),
            actual=trace.final_value,
        )

    def verify_step(
        self,
        problem: Problem,
        trace: Trace,
        step_index: int,
        candidate_value: float,
    ) -> VerificationResult:
        """
        Verify a single step in a trace.
        """
        if step_index < 0 or step_index >= len(trace.steps):
            return VerificationResult(
                correct=False,
                score=0.0,
                error_type=ErrorType.INVALID_FORMAT,
                error_message=f"Step index {step_index} out of range (0-{len(trace.steps) - 1})",
            )

        step = trace.steps[step_index]
        expected = step.output_value
        tolerance = self.default_tolerance

        correct = abs(expected - candidate_value) <= tolerance

        if correct:
            return VerificationResult(
                correct=True,
                score=1.0,
                error_type=ErrorType.NONE,
                expected=expected,
                actual=candidate_value,
                tolerance_used=tolerance,
            )

        error_type = self._classify_error(expected, candidate_value)

        return VerificationResult(
            correct=False,
            score=0.0,
            error_type=error_type,
            error_message=self._get_error_message(error_type, expected, candidate_value),
            expected=expected,
            actual=candidate_value,
            tolerance_used=tolerance,
        )

    def grade_tool_usage(
        self,
        problem: Problem,
        tool_calls: list[dict],
    ) -> list[ToolCallGrade]:
        """
        Grade tool usage for arithmetic problems.

        Arithmetic-specific grading:
        - Penalize unnecessary calculator calls for simple operations
        - Check that arithmetic tool arguments are valid numbers
        """
        grades = []

        for call in tool_calls:
            tool_name = call.get("name", "unknown")
            args = call.get("args", {})

            # Start with base validation from parent
            base_grades = super().grade_tool_usage(problem, [call])
            if base_grades and not base_grades[0].valid:
                grades.extend(base_grades)
                continue

            # Arithmetic-specific validation
            if tool_name in ["calculate", "eval", "compute"]:
                # Check if expression argument is valid
                expr = args.get("expression", "")
                if not self._is_valid_expression(expr):
                    grades.append(
                        ToolCallGrade(
                            tool_name=tool_name,
                            args=args,
                            valid=False,
                            necessary=False,
                            efficient=False,
                            penalty=0.2,
                            error_message=f"Invalid expression: {expr}",
                        )
                    )
                    continue

                # Check if this was a trivially simple calculation
                if self._is_trivial_calculation(expr):
                    grades.append(
                        ToolCallGrade(
                            tool_name=tool_name,
                            args=args,
                            valid=True,
                            necessary=False,  # Could do mentally
                            efficient=False,
                            penalty=0.1,
                            error_message="Trivial calculation could be done mentally",
                        )
                    )
                    continue

            # Valid, necessary, efficient call
            grades.append(
                ToolCallGrade(
                    tool_name=tool_name,
                    args=args,
                    valid=True,
                    necessary=True,
                    efficient=True,
                    penalty=0.0,
                )
            )

        return grades

    def _parse_answer(self, answer: str) -> Optional[float]:
        """
        Parse various answer formats into a float.

        Handles:
        - Plain numbers: "42", "-3.14", "1.5e-3"
        - Boxed LaTeX: "\\boxed{42}", "\\(\\boxed{42}\\)"
        - With surrounding text: "The answer is 42."
        """
        if not answer:
            return None

        answer = answer.strip()

        # Try to extract from boxed LaTeX
        boxed_match = re.search(r"\\boxed\{([^}]+)\}", answer)
        if boxed_match:
            answer = boxed_match.group(1).strip()

        # Remove common LaTeX wrappers
        answer = re.sub(r"\\\(|\\\)|\\\[|\\\]", "", answer)
        answer = answer.strip()

        # Try direct parsing
        try:
            return float(answer)
        except ValueError:
            pass

        # Try to extract number from text
        number_match = re.search(r"-?\d+\.?\d*(?:[eE][+-]?\d+)?", answer)
        if number_match:
            try:
                return float(number_match.group())
            except ValueError:
                pass

        return None

    def _classify_error(self, expected: float, actual: float) -> ErrorType:
        """
        Classify the type of error based on expected vs actual values.
        """
        # Sign error: same magnitude, wrong sign
        if abs(abs(expected) - abs(actual)) < self.default_tolerance:
            if expected != actual:
                return ErrorType.SIGN_ERROR

        # Rounding error: very close
        if abs(expected - actual) < 0.01:
            return ErrorType.ROUNDING_ERROR

        # Order of operations error: common pattern
        # e.g., 3 + 5 * 2 = 16 (wrong) vs 13 (correct)
        # This is heuristic - would need expression to be certain

        # Division error: result is reciprocal or off by factor
        if expected != 0 and actual != 0:
            ratio = abs(expected / actual)
            if abs(ratio - 1) > 0.1:  # Not just rounding
                if abs(ratio - round(ratio)) < 0.01:
                    return ErrorType.DIVISION_ERROR

        return ErrorType.WRONG_ANSWER

    def _get_error_message(
        self,
        error_type: ErrorType,
        expected: float,
        actual: float,
    ) -> str:
        """Generate a human-readable error message."""
        messages = {
            ErrorType.SIGN_ERROR: f"Sign error: expected {expected}, got {actual}",
            ErrorType.ROUNDING_ERROR: f"Rounding error: expected {expected}, got {actual}",
            ErrorType.DIVISION_ERROR: f"Division error: expected {expected}, got {actual}",
            ErrorType.ORDER_OF_OPS: f"Order of operations error: expected {expected}, got {actual}",
            ErrorType.WRONG_ANSWER: f"Incorrect: expected {expected}, got {actual}",
        }
        return messages.get(error_type, f"Expected {expected}, got {actual}")

    def _is_valid_expression(self, expr: str) -> bool:
        """Check if an expression string is valid for evaluation."""
        if not expr or not expr.strip():
            return False

        # Basic validation: should contain numbers and operators
        valid_pattern = r"^[\d\s\+\-\*\/\(\)\.\^]+$"
        return bool(re.match(valid_pattern, expr.strip()))

    def _is_trivial_calculation(self, expr: str) -> bool:
        """
        Check if a calculation is trivially simple.

        Trivial = single operation with small integers.
        """
        # Remove spaces
        expr = expr.replace(" ", "")

        # Check for single operation patterns
        trivial_patterns = [
            r"^\d{1,2}[\+\-]\d{1,2}$",  # e.g., "3+5", "12-7"
            r"^\d{1,2}\*\d{1,2}$",  # e.g., "3*4"
            r"^\d{1,2}\/[1-9]$",  # e.g., "8/2"
        ]

        for pattern in trivial_patterns:
            if re.match(pattern, expr):
                return True

        return False
