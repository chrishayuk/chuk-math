"""
Base verifier interface for all domains.

Verifiers are responsible for:
- Checking final answers against gold answers
- Verifying solution traces step-by-step
- Grading tool usage for efficiency
- Classifying errors
"""

from abc import ABC, abstractmethod
from typing import Optional

from chuk_math_gym.schemas.problem import Problem
from chuk_math_gym.schemas.trace import Trace
from chuk_math_gym.schemas.verification import VerificationResult, ToolCallGrade


class Verifier(ABC):
    """
    Abstract base class for domain-specific verifiers.

    Each domain (arithmetic, fractions, algebra, etc.) implements its own
    verifier that understands the semantics of that domain.

    Example usage:
        verifier = ArithmeticVerifier()
        result = verifier.verify_final(problem, "42")
        if result.correct:
            print("Correct!")
        else:
            print(f"Error: {result.error_type}")
    """

    @abstractmethod
    def verify_final(
        self,
        problem: Problem,
        candidate: str,
    ) -> VerificationResult:
        """
        Verify a final answer against the gold answer.

        Args:
            problem: The problem being verified
            candidate: The candidate answer string

        Returns:
            VerificationResult with correctness and error details
        """
        pass

    @abstractmethod
    def verify_trace(
        self,
        problem: Problem,
        trace: Trace,
    ) -> VerificationResult:
        """
        Verify a complete solution trace.

        This checks each step in the trace and provides partial credit
        for correct intermediate steps.

        Args:
            problem: The problem being solved
            trace: The solution trace to verify

        Returns:
            VerificationResult with step-level details
        """
        pass

    @abstractmethod
    def verify_step(
        self,
        problem: Problem,
        trace: Trace,
        step_index: int,
        candidate_value: float,
    ) -> VerificationResult:
        """
        Verify a single step in a trace.

        Args:
            problem: The problem being solved
            trace: The reference trace
            step_index: Index of the step to verify
            candidate_value: The candidate value for this step

        Returns:
            VerificationResult for this step
        """
        pass

    def grade_tool_usage(
        self,
        problem: Problem,
        tool_calls: list[dict],
    ) -> list[ToolCallGrade]:
        """
        Grade tool usage for validity and efficiency.

        Default implementation checks basic validity.
        Override in subclasses for domain-specific grading.

        Args:
            problem: The problem being solved
            tool_calls: List of tool call dicts with 'name' and 'args'

        Returns:
            List of ToolCallGrade for each call
        """
        grades = []
        for call in tool_calls:
            tool_name = call.get("name", "unknown")
            args = call.get("args", {})

            # Check if tool is allowed
            if problem.allowed_tools and tool_name not in problem.allowed_tools:
                grades.append(
                    ToolCallGrade(
                        tool_name=tool_name,
                        args=args,
                        valid=False,
                        necessary=False,
                        efficient=False,
                        penalty=0.5,
                        error_message=f"Tool '{tool_name}' not in allowed list",
                    )
                )
            elif problem.forbidden_tools and tool_name in problem.forbidden_tools:
                grades.append(
                    ToolCallGrade(
                        tool_name=tool_name,
                        args=args,
                        valid=False,
                        necessary=False,
                        efficient=False,
                        penalty=1.0,
                        error_message=f"Tool '{tool_name}' is forbidden",
                    )
                )
            else:
                # Basic valid call
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

    def compute_partial_credit(
        self,
        trace: Trace,
        first_error_step: Optional[int],
    ) -> float:
        """
        Compute partial credit based on correct steps.

        Args:
            trace: The solution trace
            first_error_step: Index of first incorrect step (None if all correct)

        Returns:
            Partial credit score (0.0 to 1.0)
        """
        if first_error_step is None:
            return 1.0
        if trace.total_steps == 0:
            return 0.0
        return first_error_step / trace.total_steps
