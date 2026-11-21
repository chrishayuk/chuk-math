"""
Problem schema: The canonical representation of a math task.

This module extends chuk-gym-core's Problem with math-specific fields.
"""

from enum import Enum
from typing import Any

from pydantic import Field

# Re-export core types
from chuk_gym_core import (
    Problem as CoreProblem,
    DifficultyLevel,
    ToolPolicy,
)


class DomainType(str, Enum):
    """Mathematical domains supported by chuk-math-gym."""

    ARITHMETIC = "arithmetic"
    FRACTIONS = "fractions"
    LINEAR_EQUATIONS = "linear_equations"
    WORD_PROBLEMS = "word_problems"
    QUADRATIC = "quadratic"
    GEOMETRY = "geometry"
    CALCULUS = "calculus"


class AnswerType(str, Enum):
    """How the answer should be verified."""

    EXACT = "exact"  # Must match exactly (integers, simple fractions)
    NUMERIC = "numeric"  # Numeric with tolerance (decimals)
    EXPRESSION = "expression"  # Symbolically equivalent (algebra)
    CHOICE = "choice"  # Multiple choice selection


class Problem(CoreProblem):
    """
    Math-specific problem representation.

    Extends the core Problem with math-specific fields like answer_type.

    Example:
        problem = Problem(
            id="arith_easy_12345",
            seed=12345,
            domain="arithmetic",
            difficulty=DifficultyLevel.EASY,
            prompt="What is 3 + 5 * 2?",
            expression="3 + 5 * 2",
            gold_answer="13",
            answer_type=AnswerType.EXACT,
        )
    """

    # Math-specific: how to verify the answer
    answer_type: AnswerType = Field(
        default=AnswerType.NUMERIC,
        description="How to verify the answer",
    )

    # Alias for backward compatibility
    tolerance: float | None = Field(
        default=None,
        description="Numeric tolerance for approximate answers",
    )

    @classmethod
    def generate_id(
        cls, domain: DomainType | str, difficulty: DifficultyLevel, seed: int
    ) -> str:
        """Generate a deterministic problem ID."""
        domain_str = domain.value if isinstance(domain, DomainType) else domain
        return f"{domain_str}_{difficulty.value}_{seed}"

    @classmethod
    def generate_id_from_content(cls, domain: DomainType | str, expression: str) -> str:
        """Generate a content-based ID (for problems without seeds)."""
        import hashlib

        domain_str = domain.value if isinstance(domain, DomainType) else domain
        content_hash = hashlib.md5(expression.encode()).hexdigest()[:8]
        return f"{domain_str}_{content_hash}"

    def to_prompt_dict(self) -> dict[str, Any]:
        """Export as a simple prompt dict for training."""
        return {
            "id": self.id,
            "prompt": self.prompt,
            "gold_answer": self.gold_answer,
        }

    def to_full_dict(self) -> dict[str, Any]:
        """Export full problem specification."""
        return self.model_dump(exclude_none=True)
