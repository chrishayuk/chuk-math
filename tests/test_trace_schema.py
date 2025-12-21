"""Tests for the trace schema module."""

import pytest
from chuk_math_gym.schemas.trace import (
    StepOperation,
    RuleID,
    StepRef,
    Step,
    Trace,
    LiteralArgs,
    ArithmeticArgs,
    EquationTransformArgs,
    FractionArgs,
    RewriteArgs,
    SubstitutionArgs,
    EmptyArgs,
)


class TestStepRef:
    """Tests for StepRef class."""

    def test_placeholder_name(self):
        """Test placeholder_name property."""
        ref = StepRef(step_index=0)
        assert ref.placeholder_name == "x1"

        ref2 = StepRef(step_index=5)
        assert ref2.placeholder_name == "x6"

    def test_hash(self):
        """Test __hash__ method."""
        ref1 = StepRef(step_index=0)
        ref2 = StepRef(step_index=0)

        assert hash(ref1) == hash(ref2)

        # Can use in sets
        s = {ref1, ref2}
        assert len(s) == 1

    def test_equality(self):
        """Test __eq__ method."""
        ref1 = StepRef(step_index=0)
        ref2 = StepRef(step_index=0)
        ref3 = StepRef(step_index=1)

        assert ref1 == ref2
        assert ref1 != ref3
        assert ref1 != "not a ref"


class TestStep:
    """Tests for Step class."""

    def test_basic_step(self):
        """Test creating a basic step."""
        step = Step(
            index=0,
            operation=StepOperation.ADD,
            before_state="3 + 5",
            after_state="8",
            output_value=8.0,
        )

        assert step.index == 0
        assert step.output == "x1"
        assert step.inputs == []

    def test_step_with_input_refs(self):
        """Test step with input references."""
        step = Step(
            index=2,
            operation=StepOperation.MULTIPLY,
            before_state="5 * 2",
            after_state="10",
            input_refs=[StepRef(step_index=0), StepRef(step_index=1)],
            output_value=10.0,
        )

        assert step.inputs == ["x1", "x2"]
        assert len(step.input_refs) == 2

    def test_verify_output_correct(self):
        """Test verify_output with correct value."""
        step = Step(
            index=0,
            operation=StepOperation.EVAL,
            before_state="5",
            after_state="5",
            output_value=5.0,
        )

        assert step.verify_output(5.0)
        assert step.verify_output(5.0000000001)  # Within default tolerance of 1e-9

    def test_verify_output_incorrect(self):
        """Test verify_output with incorrect value."""
        step = Step(
            index=0,
            operation=StepOperation.EVAL,
            before_state="5",
            after_state="5",
            output_value=5.0,
        )

        assert not step.verify_output(10.0)

    def test_input_refs_validation_fails_for_future_refs(self):
        """Test that input_refs validation rejects future references."""
        with pytest.raises(ValueError, match="must be earlier"):
            Step(
                index=1,
                operation=StepOperation.ADD,
                before_state="test",
                after_state="test",
                input_refs=[StepRef(step_index=2)],  # Future ref
                output_value=0.0,
            )

    def test_input_refs_validation_fails_for_same_index(self):
        """Test that input_refs validation rejects same-index references."""
        with pytest.raises(ValueError, match="must be earlier"):
            Step(
                index=1,
                operation=StepOperation.ADD,
                before_state="test",
                after_state="test",
                input_refs=[StepRef(step_index=1)],  # Same index
                output_value=0.0,
            )


class TestTrace:
    """Tests for Trace class."""

    def _make_trace(self) -> Trace:
        """Create a test trace with multiple steps."""
        steps = [
            Step(
                index=0,
                operation=StepOperation.LITERAL,
                before_state="3",
                after_state="3",
                output_value=3.0,
            ),
            Step(
                index=1,
                operation=StepOperation.LITERAL,
                before_state="5",
                after_state="5",
                output_value=5.0,
            ),
            Step(
                index=2,
                operation=StepOperation.ADD,
                before_state="3 + 5",
                after_state="8",
                input_refs=[StepRef(step_index=0), StepRef(step_index=1)],
                output_value=8.0,
            ),
        ]
        return Trace(problem_id="test", steps=steps)

    def test_computed_properties(self):
        """Test computed properties."""
        trace = self._make_trace()

        assert trace.total_steps == 3
        assert trace.total_cost == 3.0  # Default difficulty_cost is 1.0
        assert trace.final_step_index == 2
        assert trace.final_value == 8.0
        assert trace.final_placeholder == "x3"

    def test_placeholder_map(self):
        """Test placeholder_map computed property."""
        trace = self._make_trace()

        pm = trace.placeholder_map
        assert pm["x1"] == 3.0
        assert pm["x2"] == 5.0
        assert pm["x3"] == 8.0

    def test_verify_step_valid(self):
        """Test verify_step with valid index."""
        trace = self._make_trace()

        assert trace.verify_step(0, 3.0)
        assert trace.verify_step(2, 8.0)
        assert not trace.verify_step(2, 10.0)

    def test_verify_step_out_of_range(self):
        """Test verify_step with invalid index."""
        trace = self._make_trace()

        with pytest.raises(IndexError):
            trace.verify_step(-1, 0.0)

        with pytest.raises(IndexError):
            trace.verify_step(10, 0.0)

    def test_verify_final(self):
        """Test verify_final method."""
        trace = self._make_trace()

        assert trace.verify_final(8.0)
        assert not trace.verify_final(10.0)

    def test_get_step_values(self):
        """Test get_step_values method."""
        trace = self._make_trace()

        values = trace.get_step_values()
        assert values == [("x1", 3.0), ("x2", 5.0), ("x3", 8.0)]

    def test_get_checkpoint_values(self):
        """Test get_checkpoint_values method."""
        steps = [
            Step(
                index=0,
                operation=StepOperation.LITERAL,
                before_state="3",
                after_state="3",
                output_value=3.0,
            ),
            Step(
                index=1,
                operation=StepOperation.LITERAL,
                before_state="5",
                after_state="5",
                output_value=5.0,
            ),
        ]
        trace = Trace(problem_id="test", steps=steps, checkpoints=[0, 1])

        values = trace.get_checkpoint_values()
        assert values == [3.0, 5.0]

    def test_get_checkpoint_values_invalid_index(self):
        """Test get_checkpoint_values with out-of-range checkpoint."""
        steps = [
            Step(
                index=0,
                operation=StepOperation.LITERAL,
                before_state="3",
                after_state="3",
                output_value=3.0,
            ),
        ]
        trace = Trace(problem_id="test", steps=steps, checkpoints=[0, 5])  # 5 is invalid

        values = trace.get_checkpoint_values()
        assert values == [3.0]  # Only valid checkpoint

    def test_count_operations(self):
        """Test count_operations method."""
        trace = self._make_trace()

        counts = trace.count_operations()
        assert counts[StepOperation.LITERAL] == 2
        assert counts[StepOperation.ADD] == 1

    def test_get_step_by_ref_valid(self):
        """Test get_step_by_ref with valid reference."""
        trace = self._make_trace()

        ref = StepRef(step_index=1)
        step = trace.get_step_by_ref(ref)

        assert step is not None
        assert step.output_value == 5.0

    def test_get_step_by_ref_invalid(self):
        """Test get_step_by_ref with invalid reference."""
        trace = self._make_trace()

        ref = StepRef(step_index=10)
        step = trace.get_step_by_ref(ref)

        assert step is None

    def test_get_input_values(self):
        """Test get_input_values method."""
        trace = self._make_trace()

        step = trace.steps[2]  # The ADD step
        values = trace.get_input_values(step)

        assert values == [3.0, 5.0]

    def test_to_natural_language(self):
        """Test to_natural_language method."""
        trace = self._make_trace()

        nl = trace.to_natural_language()

        assert "Step 0" in nl
        assert "Step 1" in nl
        assert "Step 2" in nl
        assert "3 + 5 = 8" in nl

    def test_to_placeholder_format(self):
        """Test to_placeholder_format method."""
        trace = self._make_trace()

        fmt = trace.to_placeholder_format()

        assert "<x1>" in fmt
        assert "<x2>" in fmt
        assert "<x3>" in fmt
        assert "add" in fmt.lower()

    def test_empty_trace_final_value(self):
        """Test final_value with empty trace."""
        trace = Trace(problem_id="test", steps=[])

        assert trace.final_value == 0.0
        assert trace.final_placeholder == ""

    def test_final_step_index_out_of_range(self):
        """Test final_placeholder with out-of-range final_step_index."""
        steps = [
            Step(
                index=0,
                operation=StepOperation.LITERAL,
                before_state="3",
                after_state="3",
                output_value=3.0,
            ),
        ]
        trace = Trace(problem_id="test", steps=steps, final_step_index=10)

        # Out of range, should return defaults
        assert trace.final_placeholder == ""
        assert trace.final_value == 0.0


class TestOperationArgs:
    """Tests for operation argument types."""

    def test_literal_args(self):
        """Test LiteralArgs."""
        args = LiteralArgs(value=5.0, source="input")
        assert args.op_type == "literal"
        assert args.value == 5.0

    def test_arithmetic_args(self):
        """Test ArithmeticArgs."""
        args = ArithmeticArgs(left=3.0, right=5.0, operator="+")
        assert args.op_type == "arithmetic"
        assert args.left == 3.0

    def test_equation_transform_args(self):
        """Test EquationTransformArgs."""
        args = EquationTransformArgs(value=5, variable="y")
        assert args.op_type == "equation"
        assert args.variable == "y"

    def test_fraction_args(self):
        """Test FractionArgs."""
        args = FractionArgs(numerator=3, denominator=4, gcd=1)
        assert args.op_type == "fraction"
        assert args.numerator == 3

    def test_rewrite_args(self):
        """Test RewriteArgs."""
        args = RewriteArgs(from_expr="x+x", to_expr="2x")
        assert args.op_type == "rewrite"
        assert args.from_expr == "x+x"

    def test_substitution_args(self):
        """Test SubstitutionArgs."""
        args = SubstitutionArgs(variable="x", value=5.0)
        assert args.op_type == "substitution"
        assert args.value == 5.0

    def test_empty_args(self):
        """Test EmptyArgs."""
        args = EmptyArgs()
        assert args.op_type == "empty"


class TestStepWithTypedArgs:
    """Tests for Step with typed operation arguments."""

    def test_step_with_arithmetic_args(self):
        """Test step with ArithmeticArgs."""
        step = Step(
            index=0,
            operation=StepOperation.ADD,
            before_state="3 + 5",
            after_state="8",
            output_value=8.0,
            args=ArithmeticArgs(left=3.0, right=5.0, operator="+"),
        )

        assert step.args is not None
        assert step.args.op_type == "arithmetic"
        assert step.args.left == 3.0

    def test_step_with_equation_args(self):
        """Test step with EquationTransformArgs."""
        step = Step(
            index=0,
            operation=StepOperation.ADD_BOTH,
            before_state="x = 5",
            after_state="x + 3 = 8",
            output_value=8.0,
            rule_id=RuleID.MOVE_CONSTANT,
            args=EquationTransformArgs(value=3, variable="x"),
        )

        assert step.rule_id == RuleID.MOVE_CONSTANT
        assert step.args is not None
        assert step.args.value == 3
