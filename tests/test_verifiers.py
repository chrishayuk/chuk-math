"""Tests for chuk-math-gym verifiers."""

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
from chuk_math_gym.schemas.trace import Step, Trace, StepOperation
from chuk_math_gym.schemas.verification import ErrorType
from chuk_math_gym.verifiers.arithmetic import ArithmeticVerifier


class TestArithmeticVerifier:
    """Tests for the ArithmeticVerifier."""

    @pytest.fixture
    def verifier(self):
        """Create a verifier instance."""
        return ArithmeticVerifier()

    @pytest.fixture
    def simple_problem(self):
        """Create a simple test problem."""
        return Problem(
            id="test_1",
            seed=42,
            domain=DomainType.ARITHMETIC,
            difficulty=DifficultyLevel.EASY,
            prompt="What is 3 + 5?",
            expression="3 + 5",
            gold_answer="8",
            answer_type=AnswerType.EXACT,
        )

    def test_verify_correct_answer(self, verifier, simple_problem):
        """Test verifying a correct answer."""
        result = verifier.verify_final(simple_problem, "8")

        assert result.correct
        assert result.score == 1.0
        assert result.error_type == ErrorType.NONE
        assert result.expected == 8.0
        assert result.actual == 8.0

    def test_verify_incorrect_answer(self, verifier, simple_problem):
        """Test verifying an incorrect answer."""
        result = verifier.verify_final(simple_problem, "10")

        assert not result.correct
        assert result.score == 0.0
        assert result.error_type == ErrorType.WRONG_ANSWER
        assert result.expected == 8.0
        assert result.actual == 10.0

    def test_verify_sign_error(self, verifier):
        """Test detection of sign errors."""
        problem = Problem(
            id="test_2",
            seed=1,
            domain=DomainType.ARITHMETIC,
            difficulty=DifficultyLevel.EASY,
            prompt="What is 5?",
            gold_answer="5",
        )

        result = verifier.verify_final(problem, "-5")

        assert not result.correct
        assert result.error_type == ErrorType.SIGN_ERROR

    def test_verify_rounding_error(self, verifier):
        """Test detection of rounding errors."""
        problem = Problem(
            id="test_3",
            seed=1,
            domain=DomainType.ARITHMETIC,
            difficulty=DifficultyLevel.HARD,
            prompt="What is 10 / 3?",
            gold_answer="3.3333",
            answer_type=AnswerType.NUMERIC,
            tolerance=0.001,  # Tolerance of 0.001 to accept 3.333 vs 3.3333
        )

        result = verifier.verify_final(problem, "3.333")

        # Should be correct within tolerance
        assert result.correct

    def test_verify_with_tolerance(self, verifier):
        """Test verification with tolerance."""
        problem = Problem(
            id="test_4",
            seed=1,
            domain=DomainType.ARITHMETIC,
            difficulty=DifficultyLevel.HARD,
            prompt="What is pi?",
            gold_answer="3.14159",
            answer_type=AnswerType.NUMERIC,
            tolerance=0.001,
        )

        # Within tolerance
        result = verifier.verify_final(problem, "3.142")
        assert result.correct

        # Outside tolerance
        result = verifier.verify_final(problem, "3.15")
        assert not result.correct

    def test_verify_invalid_format(self, verifier, simple_problem):
        """Test verifying unparseable answer."""
        result = verifier.verify_final(simple_problem, "not a number")

        assert not result.correct
        assert result.error_type == ErrorType.INVALID_FORMAT

    def test_verify_boxed_latex_answer(self, verifier, simple_problem):
        """Test parsing boxed LaTeX answers."""
        result = verifier.verify_final(simple_problem, r"\boxed{8}")
        assert result.correct

        result = verifier.verify_final(simple_problem, r"\(\boxed{8}\)")
        assert result.correct

    def test_verify_answer_with_text(self, verifier, simple_problem):
        """Test extracting answer from text."""
        result = verifier.verify_final(simple_problem, "The answer is 8.")
        assert result.correct

        result = verifier.verify_final(simple_problem, "8 apples")
        assert result.correct

    def test_verify_negative_answer(self, verifier):
        """Test verifying negative answers."""
        problem = Problem(
            id="test_5",
            seed=1,
            domain=DomainType.ARITHMETIC,
            difficulty=DifficultyLevel.MEDIUM,
            prompt="What is 3 - 10?",
            gold_answer="-7",
        )

        result = verifier.verify_final(problem, "-7")
        assert result.correct

        result = verifier.verify_final(problem, "7")
        assert not result.correct
        assert result.error_type == ErrorType.SIGN_ERROR

    def test_verify_decimal_answer(self, verifier):
        """Test verifying decimal answers."""
        problem = Problem(
            id="test_6",
            seed=1,
            domain=DomainType.ARITHMETIC,
            difficulty=DifficultyLevel.HARD,
            prompt="What is 7 / 2?",
            gold_answer="3.5",
            answer_type=AnswerType.NUMERIC,
            tolerance=0.01,
        )

        result = verifier.verify_final(problem, "3.5")
        assert result.correct

        result = verifier.verify_final(problem, "3.50")
        assert result.correct

    def test_verify_scientific_notation(self, verifier):
        """Test verifying scientific notation."""
        problem = Problem(
            id="test_7",
            seed=1,
            domain=DomainType.ARITHMETIC,
            difficulty=DifficultyLevel.VERY_HARD,
            prompt="What is 1000000?",
            gold_answer="1000000",
        )

        result = verifier.verify_final(problem, "1e6")
        assert result.correct

        result = verifier.verify_final(problem, "1.0e6")
        assert result.correct


class TestArithmeticVerifierTrace:
    """Tests for trace verification."""

    @pytest.fixture
    def verifier(self):
        return ArithmeticVerifier()

    def test_verify_complete_trace(self, verifier):
        """Test verifying a complete correct trace."""
        problem = Problem(
            id="test_1",
            seed=42,
            domain=DomainType.ARITHMETIC,
            difficulty=DifficultyLevel.EASY,
            prompt="What is 3 + 5?",
            gold_answer="8",
        )

        steps = [
            Step(index=0, operation=StepOperation.LITERAL, before_state="3", after_state="3", inputs=[], output="x1", output_value=3.0),
            Step(index=1, operation=StepOperation.LITERAL, before_state="5", after_state="5", inputs=[], output="x2", output_value=5.0),
            Step(index=2, operation=StepOperation.ADD, before_state="3 + 5", after_state="8", inputs=["x1", "x2"], output="x3", output_value=8.0),
        ]

        trace = Trace(
            problem_id="test_1",
            steps=steps,
            placeholder_map={"x1": 3.0, "x2": 5.0, "x3": 8.0},
            final_placeholder="x3",
            final_value=8.0,
        )

        result = verifier.verify_trace(problem, trace)

        assert result.correct
        assert result.score == 1.0
        assert result.steps_correct == 3
        assert result.steps_total == 3

    def test_verify_trace_with_error(self, verifier):
        """Test verifying a trace with an error."""
        problem = Problem(
            id="test_2",
            seed=42,
            domain=DomainType.ARITHMETIC,
            difficulty=DifficultyLevel.EASY,
            prompt="What is 3 + 5?",
            gold_answer="8",
        )

        # Trace with wrong final value - internally consistent but wrong answer
        steps = [
            Step(index=0, operation=StepOperation.LITERAL, before_state="3", after_state="3", inputs=[], output="x1", output_value=3.0),
            Step(index=1, operation=StepOperation.LITERAL, before_state="5", after_state="5", inputs=[], output="x2", output_value=5.0),
            Step(index=2, operation=StepOperation.ADD, before_state="3 + 5", after_state="9", inputs=["x1", "x2"], output="x3", output_value=9.0),  # Wrong!
        ]

        trace = Trace(
            problem_id="test_2",
            steps=steps,
            placeholder_map={"x1": 3.0, "x2": 5.0, "x3": 9.0},  # Wrong value
            final_placeholder="x3",
            final_value=9.0,  # Wrong
        )

        result = verifier.verify_trace(problem, trace)

        # Trace is internally consistent (all steps match placeholder_map)
        # but final answer is wrong
        assert not result.correct
        # All steps are internally consistent, just the final answer is wrong
        assert result.steps_correct == 3
        assert result.steps_total == 3

    def test_verify_single_step(self, verifier):
        """Test verifying a single step."""
        problem = Problem(
            id="test_3",
            seed=42,
            domain=DomainType.ARITHMETIC,
            difficulty=DifficultyLevel.EASY,
            prompt="What is 3 + 5?",
            gold_answer="8",
        )

        steps = [
            Step(index=0, operation=StepOperation.EVAL, before_state="3 + 5", after_state="8", inputs=[], output="x1", output_value=8.0),
        ]

        trace = Trace(
            problem_id="test_3",
            steps=steps,
            placeholder_map={"x1": 8.0},
            final_placeholder="x1",
            final_value=8.0,
        )

        # Correct step
        result = verifier.verify_step(problem, trace, 0, 8.0)
        assert result.correct

        # Incorrect step
        result = verifier.verify_step(problem, trace, 0, 10.0)
        assert not result.correct


class TestArithmeticVerifierToolGrading:
    """Tests for tool usage grading."""

    @pytest.fixture
    def verifier(self):
        return ArithmeticVerifier()

    def test_grade_valid_tool_call(self, verifier):
        """Test grading a valid tool call."""
        problem = Problem(
            id="test_1",
            seed=42,
            domain=DomainType.ARITHMETIC,
            difficulty=DifficultyLevel.HARD,
            prompt="What is 123 * 456?",
            gold_answer="56088",
        )

        tool_calls = [
            {"name": "calculate", "args": {"expression": "123 * 456"}},
        ]

        grades = verifier.grade_tool_usage(problem, tool_calls)

        assert len(grades) == 1
        assert grades[0].valid
        assert grades[0].is_good_call

    def test_grade_trivial_calculation(self, verifier):
        """Test grading a trivially simple calculation."""
        problem = Problem(
            id="test_2",
            seed=42,
            domain=DomainType.ARITHMETIC,
            difficulty=DifficultyLevel.EASY,
            prompt="What is 3 + 5?",
            gold_answer="8",
        )

        tool_calls = [
            {"name": "calculate", "args": {"expression": "3+5"}},
        ]

        grades = verifier.grade_tool_usage(problem, tool_calls)

        assert len(grades) == 1
        assert grades[0].valid
        assert not grades[0].necessary  # Too simple
        assert grades[0].penalty > 0

    def test_grade_forbidden_tool(self, verifier):
        """Test grading when tool is forbidden."""
        problem = Problem(
            id="test_3",
            seed=42,
            domain=DomainType.ARITHMETIC,
            difficulty=DifficultyLevel.EASY,
            prompt="What is 3 + 5?",
            gold_answer="8",
            forbidden_tools=["calculate"],
        )

        tool_calls = [
            {"name": "calculate", "args": {"expression": "3 + 5"}},
        ]

        grades = verifier.grade_tool_usage(problem, tool_calls)

        assert len(grades) == 1
        assert not grades[0].valid
        assert grades[0].penalty > 0

    def test_grade_allowed_tool_list(self, verifier):
        """Test grading with explicit allowed tools."""
        problem = Problem(
            id="test_4",
            seed=42,
            domain=DomainType.ARITHMETIC,
            difficulty=DifficultyLevel.HARD,
            prompt="What is 100 * 50?",
            gold_answer="5000",
            allowed_tools=["add", "subtract"],  # multiply not allowed
        )

        tool_calls = [
            {"name": "multiply", "args": {"a": 100, "b": 50}},
        ]

        grades = verifier.grade_tool_usage(problem, tool_calls)

        assert len(grades) == 1
        assert not grades[0].valid


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
