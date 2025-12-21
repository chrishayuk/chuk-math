"""
Verification schema: Results of verifying answers and traces.

VerificationResult provides structured feedback on:
- Correctness (binary and scored)
- Error classification
- Partial credit from trace verification
- Tool usage grading
"""

from enum import Enum
from typing import Optional, Union
from pydantic import BaseModel, Field


# Type for tool call arguments - primitive JSON-compatible values
ToolCallArg = Union[str, int, float, bool, None]
ToolCallArgs = dict[str, ToolCallArg]


class ErrorType(str, Enum):
    """
    Classification of errors for analysis and curriculum.

    Error types help with:
    - Identifying model weaknesses
    - Generating targeted training data
    - Providing feedback to agents
    """

    NONE = "none"  # No error (correct answer)

    # General errors
    WRONG_ANSWER = "wrong_answer"  # Generic wrong answer
    INVALID_FORMAT = "invalid_format"  # Could not parse answer
    INCOMPLETE = "incomplete"  # Partial answer

    # Arithmetic errors
    SIGN_ERROR = "sign_error"  # Wrong sign (e.g., -5 instead of 5)
    ORDER_OF_OPS = "order_of_operations"  # PEMDAS violation
    DIVISION_ERROR = "division_error"  # Division mistake
    ROUNDING_ERROR = "rounding_error"  # Close but imprecise

    # Fraction errors
    WRONG_DENOMINATOR = "wrong_denominator"
    UNREDUCED = "unreduced_fraction"  # Correct but not simplified
    NUMERATOR_ERROR = "numerator_error"

    # Algebra errors
    DISTRIBUTION_ERROR = "distribution_error"
    LIKE_TERMS_ERROR = "like_terms_error"
    ISOLATION_ERROR = "isolation_error"
    COEFFICIENT_ERROR = "coefficient_error"

    # Tool errors
    TOOL_MISUSE = "tool_misuse"
    TOOL_POLICY_VIOLATION = "tool_policy_violation"


class ToolCallGrade(BaseModel):
    """
    Grading of a single tool call.

    Used to provide fine-grained feedback on tool usage:
    - Was the call valid (correct schema)?
    - Was the call necessary (not redundant)?
    - Was the call efficient (minimal cost)?
    """

    tool_name: str = Field(description="Name of the tool called")
    args: ToolCallArgs = Field(default_factory=dict, description="Arguments passed to the tool")

    # Validity
    valid: bool = Field(default=True, description="Arguments were valid for this tool")
    error_message: Optional[str] = Field(default=None, description="Error message if invalid")

    # Efficiency
    necessary: bool = Field(default=True, description="Call was needed for the solution")
    efficient: bool = Field(default=True, description="Call was not redundant or wasteful")

    # Scoring
    penalty: float = Field(default=0.0, description="Penalty for this call (0.0 = no penalty)")

    @property
    def is_good_call(self) -> bool:
        """A good call is valid, necessary, and efficient."""
        return self.valid and self.necessary and self.efficient


class VerificationResult(BaseModel):
    """
    Result of verifying an answer, trace, or step.

    This is the primary feedback mechanism from the verifier.
    It provides both binary correctness and nuanced scoring.

    Example:
        result = VerificationResult(
            correct=True,
            score=1.0,
            error_type=ErrorType.NONE,
            expected=13.0,
            actual=13.0,
        )
    """

    # Core verdict
    correct: bool = Field(description="Whether the answer is correct")

    # Scoring (0.0 to 1.0)
    score: float = Field(
        ge=0.0, le=1.0, description="Score from 0.0 (completely wrong) to 1.0 (perfect)"
    )
    partial_credit: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Credit for correct intermediate steps"
    )

    # Error classification
    error_type: ErrorType = Field(default=ErrorType.NONE, description="Type of error (if any)")
    error_message: Optional[str] = Field(
        default=None, description="Human-readable error description"
    )

    # Numeric answer details
    expected: Optional[float] = Field(default=None, description="Expected (gold) answer")
    actual: Optional[float] = Field(default=None, description="Actual (candidate) answer")
    tolerance_used: Optional[float] = Field(
        default=None, description="Tolerance used for comparison"
    )

    # Step-level details (when trace is verified)
    steps_correct: Optional[int] = Field(default=None, description="Number of correct steps")
    steps_total: Optional[int] = Field(default=None, description="Total number of steps")
    first_error_step: Optional[int] = Field(
        default=None, description="Index of first incorrect step"
    )

    # Tool usage grading
    tool_calls_made: int = Field(default=0, description="Number of tool calls made")
    tool_calls_valid: int = Field(default=0, description="Number of valid tool calls")
    tool_calls_efficient: bool = Field(
        default=True, description="Whether tool usage was efficient overall"
    )
    tool_policy_violated: bool = Field(
        default=False, description="Whether tool policy was violated"
    )
    tool_grades: list[ToolCallGrade] = Field(
        default_factory=list, description="Individual tool call grades"
    )

    def to_reward(
        self,
        correct_reward: float = 1.0,
        wrong_penalty: float = -1.0,
        partial_weight: float = 0.5,
        tool_penalty_weight: float = 0.1,
    ) -> float:
        """
        Convert verification result to a reward signal for RL.

        Args:
            correct_reward: Reward for correct answer
            wrong_penalty: Penalty for wrong answer
            partial_weight: Weight for partial credit
            tool_penalty_weight: Weight for tool penalties

        Returns:
            Float reward value
        """
        if self.correct:
            base = correct_reward
        else:
            base = wrong_penalty
            # Add partial credit for getting steps right
            base += self.partial_credit * partial_weight

        # Subtract tool penalties
        tool_penalty = sum(g.penalty for g in self.tool_grades)
        base -= tool_penalty * tool_penalty_weight

        # Extra penalty for policy violation
        if self.tool_policy_violated:
            base -= 0.5

        return base

    def to_feedback_dict(self) -> dict:
        """Export as feedback dict for agent consumption."""
        return {
            "correct": self.correct,
            "score": self.score,
            "error_type": self.error_type.value if self.error_type else None,
            "error_message": self.error_message,
            "partial_credit": self.partial_credit,
        }
