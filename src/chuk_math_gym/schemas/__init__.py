"""
Core schemas for chuk-math-gym.

Re-exports from chuk-gym-core plus math-specific extensions.
"""

# Math-specific types
from chuk_math_gym.schemas.problem import (
    Problem,
    DomainType,
    AnswerType,
)

# Re-export core types (via our modules for consistency)
from chuk_math_gym.schemas.problem import (
    DifficultyLevel,
    ToolPolicy,
)
from chuk_math_gym.schemas.trace import (
    Step,
    StepRef,
    Trace,
    StepOperation,
    RuleID,
    OperationArgs,
    LiteralArgs,
    ArithmeticArgs,
    EquationTransformArgs,
    FractionArgs,
    RewriteArgs,
    SubstitutionArgs,
    EmptyArgs,
)
from chuk_math_gym.schemas.verification import (
    VerificationResult,
    ErrorType,
    ToolCallGrade,
)

__all__ = [
    # Problem
    "Problem",
    "DomainType",
    "DifficultyLevel",
    "AnswerType",
    "ToolPolicy",
    # Trace
    "Step",
    "StepRef",
    "Trace",
    "StepOperation",
    "RuleID",
    "OperationArgs",
    "LiteralArgs",
    "ArithmeticArgs",
    "EquationTransformArgs",
    "FractionArgs",
    "RewriteArgs",
    "SubstitutionArgs",
    "EmptyArgs",
    # Verification
    "VerificationResult",
    "ErrorType",
    "ToolCallGrade",
]
