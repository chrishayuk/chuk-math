"""
Fractions domain verifier.

Handles verification of fraction answers including:
- Equivalent fractions (3/6 = 1/2)
- Reduced form checking
- Mixed number recognition
"""

import re
import math
from fractions import Fraction
from typing import Optional, Tuple

from chuk_math_gym.schemas.problem import Problem, AnswerType
from chuk_math_gym.schemas.trace import Trace
from chuk_math_gym.schemas.verification import (
    VerificationResult,
    ErrorType,
    ToolCallGrade,
)
from chuk_math_gym.verifiers.base import Verifier


class FractionsVerifier(Verifier):
    """
    Verifier for fraction domain problems.

    Supports:
    - Fraction equivalence checking (1/2 = 2/4)
    - Reduced form verification
    - Mixed number parsing (1 1/2)
    - Decimal approximation (0.5 = 1/2)
    """

    def __init__(self, require_reduced: bool = True, tolerance: float = 1e-9):
        """
        Initialize the fractions verifier.

        Args:
            require_reduced: Whether answers must be in reduced form
            tolerance: Tolerance for numeric comparisons
        """
        self.require_reduced = require_reduced
        self.tolerance = tolerance

    def verify_final(
        self,
        problem: Problem,
        candidate: str,
    ) -> VerificationResult:
        """
        Verify a fraction answer.

        Handles various formats:
        - Simple fractions: "3/4", "1/2"
        - Mixed numbers: "1 1/2", "2 3/4"
        - Whole numbers: "3", "-2"
        - Decimals: "0.5", "0.333"
        """
        # Parse candidate answer
        candidate_frac = self._parse_fraction(candidate)

        if candidate_frac is None:
            return VerificationResult(
                correct=False,
                score=0.0,
                error_type=ErrorType.INVALID_FORMAT,
                error_message=f"Could not parse '{candidate}' as a fraction",
            )

        # Parse gold answer
        gold_frac = self._parse_fraction(problem.gold_answer)

        if gold_frac is None:
            return VerificationResult(
                correct=False,
                score=0.0,
                error_type=ErrorType.INVALID_FORMAT,
                error_message=f"Invalid gold answer: {problem.gold_answer}",
            )

        # Check if fractions are equivalent
        if candidate_frac == gold_frac:
            # Check if reduced form is required
            if self.require_reduced and problem.answer_type == AnswerType.EXPRESSION:
                candidate_reduced = self._is_reduced(candidate)
                if not candidate_reduced:
                    return VerificationResult(
                        correct=False,
                        score=0.75,  # Partial credit for correct value
                        partial_credit=0.75,
                        error_type=ErrorType.UNREDUCED,
                        error_message="Answer is correct but not in lowest terms",
                        expected=float(gold_frac),
                        actual=float(candidate_frac),
                    )

            return VerificationResult(
                correct=True,
                score=1.0,
                error_type=ErrorType.NONE,
                expected=float(gold_frac),
                actual=float(candidate_frac),
            )

        # Wrong answer - classify error
        error_type = self._classify_error(gold_frac, candidate_frac, candidate)

        return VerificationResult(
            correct=False,
            score=0.0,
            error_type=error_type,
            error_message=self._get_error_message(error_type, gold_frac, candidate_frac),
            expected=float(gold_frac),
            actual=float(candidate_frac),
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

        # Check each step
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
        gold_frac = self._parse_fraction(problem.gold_answer)
        if gold_frac is None:
            return VerificationResult(
                correct=False,
                score=0.0,
                error_type=ErrorType.INVALID_FORMAT,
            )

        final_correct = abs(trace.final_value - float(gold_frac)) < self.tolerance

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

    def _parse_fraction(self, answer: str) -> Optional[Fraction]:
        """
        Parse various fraction formats into a Fraction object.

        Handles:
        - "3/4" -> Fraction(3, 4)
        - "1 1/2" -> Fraction(3, 2)
        - "3" -> Fraction(3, 1)
        - "0.5" -> Fraction(1, 2)
        - "-2/3" -> Fraction(-2, 3)
        """
        if not answer:
            return None

        answer = answer.strip()

        # Remove LaTeX wrappers
        answer = re.sub(r'\\frac\{(\-?\d+)\}\{(\d+)\}', r'\1/\2', answer)
        answer = re.sub(r'\\\(|\\\)|\\\[|\\\]', '', answer)
        answer = answer.strip()

        try:
            # Try mixed number: "1 1/2" or "1-1/2"
            mixed_match = re.match(r'^(-?\d+)\s+(\d+)/(\d+)$', answer)
            if mixed_match:
                whole = int(mixed_match.group(1))
                num = int(mixed_match.group(2))
                den = int(mixed_match.group(3))
                if whole < 0:
                    return Fraction(whole * den - num, den)
                return Fraction(whole * den + num, den)

            # Try simple fraction: "3/4"
            frac_match = re.match(r'^(-?\d+)/(-?\d+)$', answer)
            if frac_match:
                num = int(frac_match.group(1))
                den = int(frac_match.group(2))
                if den == 0:
                    return None
                return Fraction(num, den)

            # Try integer
            int_match = re.match(r'^-?\d+$', answer)
            if int_match:
                return Fraction(int(answer), 1)

            # Try decimal
            try:
                decimal_val = float(answer)
                # Use limit_denominator for reasonable fractions
                return Fraction(decimal_val).limit_denominator(1000)
            except ValueError:
                pass

            return None

        except (ValueError, ZeroDivisionError):
            return None

    def _is_reduced(self, answer: str) -> bool:
        """Check if a fraction answer is in reduced form."""
        # Parse the fraction
        frac_match = re.match(r'^(-?\d+)/(\d+)$', answer.strip())
        if not frac_match:
            # Integer or other format - considered reduced
            return True

        num = abs(int(frac_match.group(1)))
        den = int(frac_match.group(2))

        return math.gcd(num, den) == 1

    def _classify_error(
        self,
        expected: Fraction,
        actual: Fraction,
        candidate_str: str,
    ) -> ErrorType:
        """Classify the type of fraction error."""
        # Check for sign error
        if abs(expected) == abs(actual) and expected != actual:
            return ErrorType.SIGN_ERROR

        # Check for unreduced (but equivalent) - shouldn't reach here normally
        if expected == actual:
            return ErrorType.UNREDUCED

        # Check for denominator error (same numerator, wrong denominator)
        # This requires parsing the original string
        frac_match = re.match(r'^(-?\d+)/(\d+)$', candidate_str.strip())
        if frac_match:
            cand_num = int(frac_match.group(1))
            exp_num = expected.numerator

            # Same numerator in reduced form
            if cand_num == exp_num:
                return ErrorType.WRONG_DENOMINATOR

        # Check for close value (might be rounding)
        if abs(float(expected) - float(actual)) < 0.01:
            return ErrorType.ROUNDING_ERROR

        return ErrorType.WRONG_ANSWER

    def _get_error_message(
        self,
        error_type: ErrorType,
        expected: Fraction,
        actual: Fraction,
    ) -> str:
        """Generate error message."""
        exp_str = f"{expected.numerator}/{expected.denominator}" if expected.denominator != 1 else str(expected.numerator)
        act_str = f"{actual.numerator}/{actual.denominator}" if actual.denominator != 1 else str(actual.numerator)

        messages = {
            ErrorType.SIGN_ERROR: f"Sign error: expected {exp_str}, got {act_str}",
            ErrorType.WRONG_DENOMINATOR: f"Wrong denominator: expected {exp_str}, got {act_str}",
            ErrorType.UNREDUCED: f"Not in lowest terms: {act_str} should be {exp_str}",
            ErrorType.ROUNDING_ERROR: f"Close but not exact: expected {exp_str}, got {act_str}",
            ErrorType.WRONG_ANSWER: f"Incorrect: expected {exp_str}, got {act_str}",
        }

        return messages.get(error_type, f"Expected {exp_str}, got {act_str}")
