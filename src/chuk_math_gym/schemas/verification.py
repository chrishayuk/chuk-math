"""
Verification schema: Results of verifying answers and traces.

Re-exports from chuk-gym-core.
"""

# Re-export everything from core
from chuk_gym_core import (
    VerificationResult,
    ErrorType,
    ToolCallGrade,
)

__all__ = [
    "VerificationResult",
    "ErrorType",
    "ToolCallGrade",
]
