"""Tests for chuk-math-gym schemas."""

import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from chuk_math_gym.schemas.problem import (
    Problem,
    DomainType,
    DifficultyLevel,
    AnswerType,
    ToolPolicy,
)
from chuk_math_gym.schemas.trace import Step, Trace, StepOperation, StepRef
from chuk_math_gym.schemas.verification import (
    VerificationResult,
    ErrorType,
    ToolCallGrade,
)


class TestProblemSchema:
    """Tests for the Problem schema."""

    def test_create_simple_problem(self):
        """Test creating a basic problem."""
        problem = Problem(
            id="test_1",
            seed=42,
            domain=DomainType.ARITHMETIC,
            difficulty=DifficultyLevel.EASY,
            prompt="What is 3 + 5?",
            expression="3 + 5",
            gold_answer="8",
        )

        assert problem.id == "test_1"
        assert problem.seed == 42
        assert problem.domain == DomainType.ARITHMETIC
        assert problem.difficulty == DifficultyLevel.EASY
        assert problem.gold_answer == "8"

    def test_problem_defaults(self):
        """Test default values are set correctly."""
        problem = Problem(
            id="test_2",
            seed=100,
            domain=DomainType.ARITHMETIC,
            difficulty=DifficultyLevel.MEDIUM,
            prompt="Calculate: 10 * 5",
            gold_answer="50",
        )

        assert problem.answer_type == AnswerType.NUMERIC
        assert problem.tool_policy == ToolPolicy.ALLOWED
        assert problem.tolerance is None
        assert problem.tags == []
        assert problem.common_mistakes == []

    def test_generate_id(self):
        """Test ID generation."""
        id1 = Problem.generate_id(DomainType.ARITHMETIC, DifficultyLevel.EASY, 42)
        assert id1 == "arithmetic_easy_42"

        id2 = Problem.generate_id(DomainType.FRACTIONS, DifficultyLevel.HARD, 100)
        assert id2 == "fractions_hard_100"

    def test_generate_id_from_content(self):
        """Test content-based ID generation."""
        id1 = Problem.generate_id_from_content(DomainType.ARITHMETIC, "3 + 5")
        id2 = Problem.generate_id_from_content(DomainType.ARITHMETIC, "3 + 5")
        id3 = Problem.generate_id_from_content(DomainType.ARITHMETIC, "3 + 6")

        # Same content should produce same ID
        assert id1 == id2
        # Different content should produce different ID
        assert id1 != id3

    def test_problem_with_tolerance(self):
        """Test problem with numeric tolerance."""
        problem = Problem(
            id="test_3",
            seed=1,
            domain=DomainType.ARITHMETIC,
            difficulty=DifficultyLevel.HARD,
            prompt="What is 10 / 3?",
            expression="10 / 3",
            gold_answer="3.3333",
            answer_type=AnswerType.NUMERIC,
            tolerance=0.0001,
        )

        assert problem.tolerance == 0.0001
        assert problem.answer_type == AnswerType.NUMERIC

    def test_problem_with_tool_restrictions(self):
        """Test problem with tool policy."""
        problem = Problem(
            id="test_4",
            seed=1,
            domain=DomainType.ARITHMETIC,
            difficulty=DifficultyLevel.MEDIUM,
            prompt="Mental math: 7 * 8",
            gold_answer="56",
            tool_policy=ToolPolicy.FORBIDDEN,
        )

        assert problem.tool_policy == ToolPolicy.FORBIDDEN

    def test_to_prompt_dict(self):
        """Test exporting as prompt dict."""
        problem = Problem(
            id="test_5",
            seed=1,
            domain=DomainType.ARITHMETIC,
            difficulty=DifficultyLevel.EASY,
            prompt="What is 2 + 2?",
            gold_answer="4",
        )

        d = problem.to_prompt_dict()
        assert d["id"] == "test_5"
        assert d["prompt"] == "What is 2 + 2?"
        assert d["gold_answer"] == "4"


class TestStepSchema:
    """Tests for the Step schema."""

    def test_create_literal_step(self):
        """Test creating a literal step."""
        step = Step(
            index=0,
            operation=StepOperation.LITERAL,
            before_state="5",
            after_state="5.0",
            inputs=[],
            output="x1",
            output_value=5.0,
        )

        assert step.index == 0
        assert step.operation == StepOperation.LITERAL
        assert step.output == "x1"
        assert step.output_value == 5.0

    def test_create_eval_step(self):
        """Test creating an evaluation step."""
        step = Step(
            index=2,
            operation=StepOperation.ADD,
            before_state="3 + 5",
            after_state="8",
            input_refs=[StepRef(step_index=0), StepRef(step_index=1)],
            output_value=8.0,
        )

        assert step.operation == StepOperation.ADD
        assert step.inputs == ["x1", "x2"]  # Backward compat computed property
        assert step.output == "x3"  # Computed from index

    def test_verify_output(self):
        """Test step output verification."""
        step = Step(
            index=0,
            operation=StepOperation.EVAL,
            before_state="3 + 5",
            after_state="8",
            inputs=[],
            output="x1",
            output_value=8.0,
        )

        assert step.verify_output(8.0)
        assert step.verify_output(8.0000001, tolerance=1e-6)
        assert not step.verify_output(9.0)


class TestTraceSchema:
    """Tests for the Trace schema."""

    def test_create_simple_trace(self):
        """Test creating a simple trace."""
        steps = [
            Step(
                index=0,
                operation=StepOperation.LITERAL,
                before_state="3",
                after_state="3.0",
                inputs=[],
                output="x1",
                output_value=3.0,
            ),
            Step(
                index=1,
                operation=StepOperation.LITERAL,
                before_state="5",
                after_state="5.0",
                inputs=[],
                output="x2",
                output_value=5.0,
            ),
            Step(
                index=2,
                operation=StepOperation.ADD,
                before_state="3 + 5",
                after_state="8",
                inputs=["x1", "x2"],
                output="x3",
                output_value=8.0,
            ),
        ]

        trace = Trace(
            problem_id="test_1",
            steps=steps,
            placeholder_map={"x1": 3.0, "x2": 5.0, "x3": 8.0},
            final_placeholder="x3",
            final_value=8.0,
        )

        assert trace.total_steps == 3
        assert trace.final_value == 8.0

    def test_verify_final(self):
        """Test final answer verification."""
        # Create a trace with at least one step (final_value is now computed from steps)
        steps = [
            Step(
                index=0,
                operation=StepOperation.LITERAL,
                before_state="42",
                after_state="42.0",
                input_refs=[],
                output_value=42.0,
            )
        ]
        trace = Trace(
            problem_id="test_1",
            steps=steps,
        )

        assert trace.verify_final(42.0)
        assert trace.verify_final(42.00000001, tolerance=1e-6)
        assert not trace.verify_final(43.0)

    def test_total_cost(self):
        """Test total cost calculation."""
        steps = [
            Step(
                index=0,
                operation=StepOperation.LITERAL,
                before_state="5",
                after_state="5.0",
                inputs=[],
                output="x1",
                output_value=5.0,
                difficulty_cost=0.5,
            ),
            Step(
                index=1,
                operation=StepOperation.EVAL,
                before_state="5 * 2",
                after_state="10",
                inputs=["x1"],
                output="x2",
                output_value=10.0,
                difficulty_cost=1.5,
            ),
        ]

        trace = Trace(
            problem_id="test_1",
            steps=steps,
            placeholder_map={"x1": 5.0, "x2": 10.0},
            final_placeholder="x2",
            final_value=10.0,
        )

        assert trace.total_cost == 2.0

    def test_count_operations(self):
        """Test operation counting."""
        steps = [
            Step(index=0, operation=StepOperation.LITERAL, before_state="3", after_state="3", inputs=[], output="x1", output_value=3.0),
            Step(index=1, operation=StepOperation.LITERAL, before_state="5", after_state="5", inputs=[], output="x2", output_value=5.0),
            Step(index=2, operation=StepOperation.ADD, before_state="3+5", after_state="8", inputs=["x1", "x2"], output="x3", output_value=8.0),
            Step(index=3, operation=StepOperation.LITERAL, before_state="2", after_state="2", inputs=[], output="x4", output_value=2.0),
            Step(index=4, operation=StepOperation.MULTIPLY, before_state="8*2", after_state="16", inputs=["x3", "x4"], output="x5", output_value=16.0),
        ]

        trace = Trace(
            problem_id="test_1",
            steps=steps,
            placeholder_map={"x1": 3.0, "x2": 5.0, "x3": 8.0, "x4": 2.0, "x5": 16.0},
            final_placeholder="x5",
            final_value=16.0,
        )

        counts = trace.count_operations()
        assert counts[StepOperation.LITERAL] == 3
        assert counts[StepOperation.ADD] == 1
        assert counts[StepOperation.MULTIPLY] == 1


class TestVerificationResultSchema:
    """Tests for the VerificationResult schema."""

    def test_correct_result(self):
        """Test a correct verification result."""
        result = VerificationResult(
            correct=True,
            score=1.0,
            error_type=ErrorType.NONE,
            expected=42.0,
            actual=42.0,
        )

        assert result.correct
        assert result.score == 1.0
        assert result.error_type == ErrorType.NONE

    def test_incorrect_result(self):
        """Test an incorrect verification result."""
        result = VerificationResult(
            correct=False,
            score=0.0,
            error_type=ErrorType.SIGN_ERROR,
            error_message="Sign error: expected 5, got -5",
            expected=5.0,
            actual=-5.0,
        )

        assert not result.correct
        assert result.score == 0.0
        assert result.error_type == ErrorType.SIGN_ERROR

    def test_partial_credit(self):
        """Test result with partial credit."""
        result = VerificationResult(
            correct=False,
            score=0.5,
            partial_credit=0.5,
            error_type=ErrorType.WRONG_ANSWER,
            steps_correct=3,
            steps_total=6,
            first_error_step=3,
        )

        assert result.partial_credit == 0.5
        assert result.steps_correct == 3
        assert result.first_error_step == 3

    def test_to_reward_correct(self):
        """Test reward calculation for correct answer."""
        result = VerificationResult(
            correct=True,
            score=1.0,
        )

        reward = result.to_reward(correct_reward=1.0, wrong_penalty=-1.0)
        assert reward == 1.0

    def test_to_reward_incorrect(self):
        """Test reward calculation for incorrect answer."""
        result = VerificationResult(
            correct=False,
            score=0.0,
            partial_credit=0.5,
        )

        reward = result.to_reward(
            correct_reward=1.0,
            wrong_penalty=-1.0,
            partial_weight=0.5,
        )
        # -1.0 + (0.5 * 0.5) = -0.75
        assert reward == -0.75

    def test_to_reward_with_tool_penalty(self):
        """Test reward with tool penalties."""
        result = VerificationResult(
            correct=True,
            score=1.0,
            tool_grades=[
                ToolCallGrade(tool_name="calc", args={}, penalty=0.1),
                ToolCallGrade(tool_name="calc", args={}, penalty=0.1),
            ],
        )

        reward = result.to_reward(
            correct_reward=1.0,
            tool_penalty_weight=0.1,
        )
        # 1.0 - (0.2 * 0.1) = 0.98
        assert abs(reward - 0.98) < 0.001


class TestToolCallGrade:
    """Tests for ToolCallGrade schema."""

    def test_good_call(self):
        """Test a good tool call."""
        grade = ToolCallGrade(
            tool_name="calculate",
            args={"expression": "3 + 5"},
            valid=True,
            necessary=True,
            efficient=True,
            penalty=0.0,
        )

        assert grade.is_good_call

    def test_bad_call(self):
        """Test a bad tool call."""
        grade = ToolCallGrade(
            tool_name="calculate",
            args={"expression": "1 + 1"},
            valid=True,
            necessary=False,  # Trivial calculation
            efficient=False,
            penalty=0.1,
        )

        assert not grade.is_good_call


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
