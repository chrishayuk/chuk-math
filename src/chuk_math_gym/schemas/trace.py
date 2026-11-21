"""
Trace schema: Machine-checkable solution traces.

Re-exports from chuk-gym-core with math-specific extensions.
"""

from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field

# Re-export core types
from chuk_gym_core import (
    Step,
    StepRef,
    Trace,
    StepOperation,
)

# Also re-export RuleID enum for math-specific rules
from chuk_gym_core.schemas.trace import StepOperation as CoreStepOperation


class RuleID(str):
    """
    Identifies specific mathematical rules applied in steps.

    Using constants instead of magic strings enables:
    - IDE autocomplete
    - Easy discovery of all rules
    """

    # Arithmetic rules
    UNARY_NEGATION = "unary_negation"
    ORDER_OF_OPERATIONS = "order_of_operations"

    # Fraction rules
    FIND_GCD = "find_gcd"
    FIND_LCM = "find_lcm"
    REDUCE_NUMERATOR = "reduce_numerator"
    REDUCE_DENOMINATOR = "reduce_denominator"
    FORM_FRACTION = "form_fraction"
    CONVERT_FRACTION = "convert_fraction"
    ADD_FRACTIONS = "add_fractions"
    SUBTRACT_FRACTIONS = "subtract_fractions"
    MULTIPLY_FRACTIONS = "multiply_fractions"
    DIVIDE_FRACTIONS = "divide_fractions"
    SIMPLIFY_RESULT = "simplify_result"

    # Equation rules
    COLLECT_VARIABLES = "collect_variables"
    MOVE_CONSTANT = "move_constant"
    ISOLATE_VARIABLE = "isolate_variable"
    DISTRIBUTE_COEFFICIENT = "distribute_coefficient"
    COMBINE_TERMS = "combine_terms"


# --- Operation-specific argument types for math ---


class LiteralArgs(BaseModel):
    """Arguments for LITERAL operation (introducing a constant)."""

    op_type: Literal["literal"] = "literal"
    value: float = Field(description="The literal value")
    source: str | None = Field(default=None, description="Where this value came from")


class ArithmeticArgs(BaseModel):
    """Arguments for arithmetic operations (ADD, SUBTRACT, MULTIPLY, DIVIDE, POWER)."""

    op_type: Literal["arithmetic"] = "arithmetic"
    left: float = Field(description="Left operand")
    right: float = Field(description="Right operand")
    operator: str = Field(description="The operator symbol (+, -, *, /, ^)")


class EquationTransformArgs(BaseModel):
    """Arguments for equation transformation operations (ADD_BOTH, SUB_BOTH, etc.)."""

    op_type: Literal["equation"] = "equation"
    value: int | float | str = Field(description="Value applied to both sides")
    variable: str = Field(default="x", description="Variable being solved for")


class FractionArgs(BaseModel):
    """Arguments for fraction operations."""

    op_type: Literal["fraction"] = "fraction"
    numerator: int | None = Field(default=None)
    denominator: int | None = Field(default=None)
    gcd: int | None = Field(default=None, description="GCD if reducing")
    lcm: int | None = Field(default=None, description="LCM if finding common denominator")


class RewriteArgs(BaseModel):
    """Arguments for algebraic rewrite operations."""

    op_type: Literal["rewrite"] = "rewrite"
    from_expr: str = Field(description="Expression before rewrite")
    to_expr: str = Field(description="Expression after rewrite")


class SubstitutionArgs(BaseModel):
    """Arguments for substitution operations."""

    op_type: Literal["substitution"] = "substitution"
    variable: str = Field(description="Variable being substituted")
    value: float = Field(description="Value to substitute")


class EmptyArgs(BaseModel):
    """For operations that don't need specific arguments."""

    op_type: Literal["empty"] = "empty"


# Discriminated union of all argument types
OperationArgs = Annotated[
    Union[
        LiteralArgs,
        ArithmeticArgs,
        EquationTransformArgs,
        FractionArgs,
        RewriteArgs,
        SubstitutionArgs,
        EmptyArgs,
    ],
    Field(discriminator="op_type"),
]


# Re-export everything
__all__ = [
    # Core types
    "Step",
    "StepRef",
    "Trace",
    "StepOperation",
    # Math-specific
    "RuleID",
    "LiteralArgs",
    "ArithmeticArgs",
    "EquationTransformArgs",
    "FractionArgs",
    "RewriteArgs",
    "SubstitutionArgs",
    "EmptyArgs",
    "OperationArgs",
]
