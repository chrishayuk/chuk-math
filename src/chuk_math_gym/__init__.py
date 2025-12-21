"""
chuk-math-gym: A verifiable reasoning and tool-use training environment for math.

This package provides:
- Problem generation with deterministic seeding
- Machine-checkable solution traces
- Local verification with partial credit
- Gym-style RL interface (reset/step)
- Tool-use policy enforcement

Designed for training LLM agents on mathematical reasoning with verifiable rewards.
"""

from chuk_math_gym.schemas.problem import (
    Problem,
    DomainType,
    DifficultyLevel,
    AnswerType,
    ToolPolicy,
)
from chuk_math_gym.schemas.trace import Step, Trace, StepOperation
from chuk_math_gym.schemas.verification import (
    VerificationResult,
    ErrorType,
    ToolCallGrade,
)
from chuk_math_gym.verifiers.base import Verifier
from chuk_math_gym.env.base import MathGymEnv

__version__ = "0.1.0"

__all__ = [
    # Problem
    "Problem",
    "DomainType",
    "DifficultyLevel",
    "AnswerType",
    "ToolPolicy",
    # Trace
    "Step",
    "Trace",
    "StepOperation",
    # Verification
    "VerificationResult",
    "ErrorType",
    "ToolCallGrade",
    # Verifier
    "Verifier",
    # Environment
    "MathGymEnv",
]
