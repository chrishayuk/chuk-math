"""
Trace schema: Machine-checkable solution traces.

A Trace is a sequence of Steps that transform the initial problem state
into the final answer. Each Step is verifiable independently, enabling:
- Partial credit scoring
- Step-level RL rewards
- Error classification at specific steps
- Curriculum based on step difficulty
"""

from enum import Enum
from typing import Optional, Union, Annotated, Literal
from pydantic import BaseModel, Field, computed_field, field_validator, model_validator


class StepOperation(str, Enum):
    """
    Operations in the Step DSL.

    These are the primitive operations that can appear in solution traces.
    Each domain extends this with domain-specific operations.
    """

    # Core evaluation operations
    EVAL = "eval"  # Evaluate a sub-expression numerically
    SIMPLIFY = "simplify"  # Reduce to canonical form
    LITERAL = "literal"  # Introduce a literal value

    # Arithmetic operations
    ADD = "add"
    SUBTRACT = "subtract"
    MULTIPLY = "multiply"
    DIVIDE = "divide"
    POWER = "power"

    # Algebraic rewrites
    REWRITE = "rewrite"  # Apply a general transformation rule
    DISTRIBUTE = "distribute"  # a(b+c) -> ab + ac
    FACTOR = "factor"  # ab + ac -> a(b+c)
    COMBINE_LIKE = "combine_like_terms"

    # Equation operations
    ADD_BOTH = "add_both_sides"
    SUB_BOTH = "subtract_both_sides"
    MUL_BOTH = "multiply_both_sides"
    DIV_BOTH = "divide_both_sides"
    ISOLATE = "isolate"

    # Validation operations
    SUBSTITUTE = "substitute"  # Plug in a value
    ASSERT = "assert"  # Check a condition holds

    # Fraction operations
    REDUCE = "reduce_fraction"
    COMMON_DENOM = "common_denominator"
    INVERT = "invert_fraction"

    # Word problem operations
    EXTRACT_VARS = "extract_variables"
    BUILD_EQ = "build_equation"
    MAP_RESULT = "map_result"  # Map numeric result to answer


class RuleID(str, Enum):
    """
    Identifies specific mathematical rules applied in steps.

    Using an enum instead of magic strings enables:
    - IDE autocomplete
    - Compile-time validation
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


class StepRef(BaseModel):
    """
    Type-safe reference to a previous step's output.

    Replaces magic string placeholders like "x1", "x2" with
    validated index-based references.

    Example:
        step.input_refs = [StepRef(step_index=0), StepRef(step_index=1)]
        # References outputs from steps 0 and 1
    """

    step_index: int = Field(ge=0, description="Index of referenced step")

    @property
    def placeholder_name(self) -> str:
        """For backward compatibility with string-based systems."""
        return f"x{self.step_index + 1}"

    def __hash__(self):
        return hash(self.step_index)

    def __eq__(self, other):
        if isinstance(other, StepRef):
            return self.step_index == other.step_index
        return False


# --- Operation-specific argument types ---


class LiteralArgs(BaseModel):
    """Arguments for LITERAL operation (introducing a constant)."""

    op_type: Literal["literal"] = "literal"
    value: float = Field(description="The literal value")
    source: Optional[str] = Field(default=None, description="Where this value came from")


class ArithmeticArgs(BaseModel):
    """Arguments for arithmetic operations (ADD, SUBTRACT, MULTIPLY, DIVIDE, POWER)."""

    op_type: Literal["arithmetic"] = "arithmetic"
    left: float = Field(description="Left operand")
    right: float = Field(description="Right operand")
    operator: str = Field(description="The operator symbol (+, -, *, /, ^)")


class EquationTransformArgs(BaseModel):
    """Arguments for equation transformation operations (ADD_BOTH, SUB_BOTH, etc.)."""

    op_type: Literal["equation"] = "equation"
    value: Union[int, float, str] = Field(description="Value applied to both sides")
    variable: str = Field(default="x", description="Variable being solved for")


class FractionArgs(BaseModel):
    """Arguments for fraction operations."""

    op_type: Literal["fraction"] = "fraction"
    numerator: Optional[int] = Field(default=None)
    denominator: Optional[int] = Field(default=None)
    gcd: Optional[int] = Field(default=None, description="GCD if reducing")
    lcm: Optional[int] = Field(default=None, description="LCM if finding common denominator")


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


class Step(BaseModel):
    """
    A single step in a solution trace.

    Each step represents an atomic transformation from one state to another.
    Steps are designed to be machine-verifiable: given the inputs and operation,
    the output should be deterministically computable.

    Example (arithmetic):
        Step(
            index=2,
            operation=StepOperation.MULTIPLY,
            before_state="5 * 2",
            after_state="10",
            input_refs=[StepRef(step_index=0), StepRef(step_index=1)],
            output_value=10.0,
            args=ArithmeticArgs(left=5.0, right=2.0, operator="*"),
        )
    """

    index: int = Field(description="Step number (0-indexed)")
    operation: StepOperation = Field(description="Operation performed")

    # State transition
    before_state: str = Field(description="Expression/state before this step")
    after_state: str = Field(description="Expression/state after this step")

    # Operation details - typed!
    rule_id: Optional[RuleID] = Field(default=None, description="Specific rule applied")
    args: Optional[OperationArgs] = Field(
        default=None, description="Operation-specific arguments (typed)"
    )

    # Type-safe step references
    input_refs: list[StepRef] = Field(default_factory=list, description="References to input steps")

    # Output value
    output_value: float = Field(description="Numeric value of output")

    # Metadata
    difficulty_cost: float = Field(default=1.0, description="Relative difficulty/cost of this step")
    common_mistake_here: Optional[str] = Field(
        default=None, description="Common error type at this step"
    )

    # --- Computed properties for backward compatibility ---

    @computed_field
    @property
    def output(self) -> str:
        """Backward compatible placeholder name."""
        return f"x{self.index + 1}"

    @computed_field
    @property
    def inputs(self) -> list[str]:
        """Backward compatible input placeholder names."""
        return [ref.placeholder_name for ref in self.input_refs]

    def verify_output(self, candidate: float, tolerance: float = 1e-9) -> bool:
        """Check if a candidate value matches this step's output."""
        return abs(self.output_value - candidate) < tolerance

    @field_validator("input_refs")
    @classmethod
    def validate_input_refs(cls, refs: list[StepRef], info) -> list[StepRef]:
        """Ensure input references point to earlier steps."""
        index = info.data.get("index", 0)
        for ref in refs:
            if ref.step_index >= index:
                raise ValueError(
                    f"Input reference to step {ref.step_index} "
                    f"must be earlier than current step {index}"
                )
        return refs


class Trace(BaseModel):
    """
    Complete solution trace for a problem.

    A Trace contains all steps needed to solve a problem, plus metadata
    for verification and reward shaping.

    The placeholder_map is now a computed property (not stored),
    derived from the steps list.

    Example:
        trace = Trace(
            problem_id="arith_easy_12345",
            steps=[...],
            final_step_index=2,
        )
        # trace.placeholder_map computed automatically
        # trace.final_value computed from steps[final_step_index]
    """

    problem_id: str = Field(description="ID of the problem this trace solves")
    steps: list[Step] = Field(description="Ordered list of solution steps")

    # Checkpoints for partial credit / reward shaping
    checkpoints: list[int] = Field(
        default_factory=list, description="Step indices that are key milestones"
    )

    # Final answer reference
    final_step_index: int = Field(
        default=-1, description="Index of final answer step (-1 means last step)"
    )

    @model_validator(mode="after")
    def set_final_step_default(self) -> "Trace":
        """Set final_step_index to last step if not specified."""
        if self.final_step_index == -1 and self.steps:
            object.__setattr__(self, "final_step_index", len(self.steps) - 1)
        return self

    # --- Computed properties ---

    @computed_field
    @property
    def total_steps(self) -> int:
        """Total number of steps in the trace."""
        return len(self.steps)

    @computed_field
    @property
    def total_cost(self) -> float:
        """Sum of difficulty costs across all steps."""
        return sum(step.difficulty_cost for step in self.steps)

    @computed_field
    @property
    def placeholder_map(self) -> dict[str, float]:
        """
        Backward compatible placeholder mapping.

        Computed from steps instead of stored redundantly.
        """
        return {step.output: step.output_value for step in self.steps}

    @computed_field
    @property
    def final_placeholder(self) -> str:
        """Backward compatible final placeholder name."""
        if self.steps and 0 <= self.final_step_index < len(self.steps):
            return self.steps[self.final_step_index].output
        return ""

    @computed_field
    @property
    def final_value(self) -> float:
        """Numeric value of final answer."""
        if self.steps and 0 <= self.final_step_index < len(self.steps):
            return self.steps[self.final_step_index].output_value
        return 0.0

    # --- Methods ---

    def verify_step(self, step_index: int, candidate_value: float, tolerance: float = 1e-9) -> bool:
        """Verify a single step's output."""
        if step_index < 0 or step_index >= len(self.steps):
            raise IndexError(f"Step index {step_index} out of range")
        return self.steps[step_index].verify_output(candidate_value, tolerance)

    def verify_final(self, candidate: float, tolerance: float = 1e-9) -> bool:
        """Verify the final answer."""
        return abs(self.final_value - candidate) < tolerance

    def get_step_values(self) -> list[tuple[str, float]]:
        """Get all (placeholder, value) pairs in step order."""
        return [(step.output, step.output_value) for step in self.steps]

    def get_checkpoint_values(self) -> list[float]:
        """Get values at checkpoint steps (for partial credit)."""
        return [self.steps[i].output_value for i in self.checkpoints if i < len(self.steps)]

    def count_operations(self) -> dict[StepOperation, int]:
        """Count occurrences of each operation type."""
        counts: dict[StepOperation, int] = {}
        for step in self.steps:
            counts[step.operation] = counts.get(step.operation, 0) + 1
        return counts

    def get_step_by_ref(self, ref: StepRef) -> Optional[Step]:
        """Get a step by its reference."""
        if 0 <= ref.step_index < len(self.steps):
            return self.steps[ref.step_index]
        return None

    def get_input_values(self, step: Step) -> list[float]:
        """Get input values for a step from its references."""
        return [
            self.steps[ref.step_index].output_value
            for ref in step.input_refs
            if ref.step_index < len(self.steps)
        ]

    def to_natural_language(self) -> str:
        """Convert trace to natural language explanation."""
        lines = []
        for step in self.steps:
            lines.append(f"Step {step.index}: {step.before_state} = {step.after_state}")
        return "\n".join(lines)

    def to_placeholder_format(self) -> str:
        """Convert trace to placeholder format (machine-readable)."""
        lines = []
        for step in self.steps:
            if step.input_refs:
                inputs_str = ", ".join(f"<{ref.placeholder_name}>" for ref in step.input_refs)
                lines.append(
                    f"STEP {step.index}: ({inputs_str}) {step.operation.value} = <{step.output}>"
                )
            else:
                lines.append(f"STEP {step.index}: <{step.output}> = {step.output_value}")
        return "\n".join(lines)
