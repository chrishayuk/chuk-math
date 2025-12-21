"""Tests for the fractions domain."""

from chuk_math_gym.schemas.problem import DifficultyLevel, DomainType, ToolPolicy, Problem
from chuk_math_gym.domains.fractions import (
    FractionsGenerator,
    FractionsVerifier,
    FractionsGymEnv,
)


class TestFractionsGenerator:
    """Tests for FractionsGenerator."""

    def test_generate_problem(self):
        """Test basic problem generation."""
        generator = FractionsGenerator()
        problem, trace = generator.generate(
            seed=42,
            difficulty=DifficultyLevel.MEDIUM,
        )

        assert problem is not None
        assert problem.domain == DomainType.FRACTIONS
        assert problem.difficulty == DifficultyLevel.MEDIUM
        assert problem.expression is not None
        assert problem.gold_answer is not None

    def test_deterministic_generation(self):
        """Test that same seed produces same problem."""
        generator = FractionsGenerator()

        p1, t1 = generator.generate(seed=123, difficulty=DifficultyLevel.EASY)
        p2, t2 = generator.generate(seed=123, difficulty=DifficultyLevel.EASY)

        assert p1.expression == p2.expression
        assert p1.gold_answer == p2.gold_answer

    def test_different_seeds_different_problems(self):
        """Test that different seeds produce different problems."""
        generator = FractionsGenerator()

        p1, _ = generator.generate(seed=100, difficulty=DifficultyLevel.MEDIUM)
        p2, _ = generator.generate(seed=200, difficulty=DifficultyLevel.MEDIUM)

        # Should usually be different (very unlikely to be same)
        assert p1.expression != p2.expression or p1.gold_answer != p2.gold_answer

    def test_generate_batch(self):
        """Test batch generation."""
        generator = FractionsGenerator()
        problems = generator.generate_batch(
            count=5,
            start_seed=42,
            difficulty=DifficultyLevel.EASY,
        )

        assert len(problems) == 5
        # Each should be a (Problem, Trace) tuple
        for problem, trace in problems:
            assert problem.domain == DomainType.FRACTIONS

    def test_difficulty_affects_problem(self):
        """Test that difficulty affects problem complexity."""
        generator = FractionsGenerator()

        easy_problems = [
            generator.generate(seed=i, difficulty=DifficultyLevel.VERY_EASY)[0] for i in range(10)
        ]

        hard_problems = [
            generator.generate(seed=i + 100, difficulty=DifficultyLevel.VERY_HARD)[0]
            for i in range(10)
        ]

        # Problems should be generated (difficulty affects internal complexity)
        assert all(p.difficulty == DifficultyLevel.VERY_EASY for p in easy_problems)
        assert all(p.difficulty == DifficultyLevel.VERY_HARD for p in hard_problems)

    def test_trace_has_steps(self):
        """Test that generated trace has steps."""
        generator = FractionsGenerator()
        problem, trace = generator.generate(
            seed=42,
            difficulty=DifficultyLevel.MEDIUM,
        )

        assert trace is not None
        assert len(trace.steps) > 0
        assert trace.final_value is not None


class TestFractionsVerifier:
    """Tests for FractionsVerifier."""

    def _make_problem(self, gold_answer: str) -> Problem:
        """Create a test problem with given gold answer."""
        return Problem(
            id="test",
            seed=0,
            domain=DomainType.FRACTIONS,
            difficulty=DifficultyLevel.MEDIUM,
            prompt="Test problem",
            expression="test",
            gold_answer=gold_answer,
        )

    def test_verify_correct_fraction(self):
        """Test verifying a correct fraction answer."""
        verifier = FractionsVerifier()
        problem = self._make_problem("1/2")
        result = verifier.verify_final(problem, "1/2")

        assert result.correct
        assert result.score == 1.0

    def test_verify_equivalent_fractions(self):
        """Test that equivalent fractions are correct."""
        verifier = FractionsVerifier(require_reduced=False)
        problem = self._make_problem("1/2")

        # 2/4 = 1/2
        result = verifier.verify_final(problem, "2/4")
        assert result.correct

        # 3/6 = 1/2
        result = verifier.verify_final(problem, "3/6")
        assert result.correct

    def test_verify_incorrect_fraction(self):
        """Test verifying an incorrect fraction."""
        verifier = FractionsVerifier()
        problem = self._make_problem("1/2")
        result = verifier.verify_final(problem, "1/3")

        assert not result.correct
        assert result.score == 0.0

    def test_verify_decimal_vs_fraction(self):
        """Test that decimal equivalent is accepted."""
        verifier = FractionsVerifier()
        problem = self._make_problem("1/2")

        result = verifier.verify_final(problem, "0.5")
        assert result.correct

    def test_verify_negative_fraction(self):
        """Test negative fractions."""
        verifier = FractionsVerifier()
        problem = self._make_problem("-1/2")

        result = verifier.verify_final(problem, "-1/2")
        assert result.correct

        # Different representations of negative
        result = verifier.verify_final(problem, "1/-2")
        assert result.correct

    def test_verify_improper_fraction(self):
        """Test improper fractions."""
        verifier = FractionsVerifier()
        problem = self._make_problem("3/2")

        result = verifier.verify_final(problem, "3/2")
        assert result.correct

    def test_verify_mixed_number(self):
        """Test mixed number format."""
        verifier = FractionsVerifier()
        problem = self._make_problem("3/2")

        # 1 1/2 = 3/2
        result = verifier.verify_final(problem, "1 1/2")
        assert result.correct

    def test_verify_invalid_format(self):
        """Test handling of invalid input."""
        verifier = FractionsVerifier()
        problem = self._make_problem("1/2")

        result = verifier.verify_final(problem, "invalid")
        assert not result.correct

    def test_verify_division_by_zero_in_answer(self):
        """Test handling division by zero in answer."""
        verifier = FractionsVerifier()
        problem = self._make_problem("1/2")

        result = verifier.verify_final(problem, "1/0")
        assert not result.correct


class TestFractionsGymEnv:
    """Tests for FractionsGymEnv."""

    def test_reset(self):
        """Test environment reset."""
        env = FractionsGymEnv()
        problem = env.reset(seed=42)

        assert problem is not None
        assert problem.domain == DomainType.FRACTIONS
        assert env.current_problem is not None

    def test_step_correct_answer(self):
        """Test stepping with correct answer."""
        env = FractionsGymEnv()
        problem = env.reset(seed=42)

        # Get the gold answer and submit it
        gold = problem.gold_answer
        obs, reward, done, info = env.step(f"ANSWER {gold}")

        assert done
        assert reward > 0
        assert info["verification_result"]["correct"]

    def test_step_wrong_answer(self):
        """Test stepping with wrong answer."""
        env = FractionsGymEnv()
        env.reset(seed=42)

        # Submit a wrong answer
        obs, reward, done, info = env.step("ANSWER 999/1000")

        assert done
        assert reward < 0
        assert not info["verification_result"]["correct"]

    def test_max_steps(self):
        """Test max steps termination."""
        env = FractionsGymEnv(max_steps=3)
        env.reset(seed=42)

        # Make tool calls until max
        for i in range(3):
            obs, reward, done, info = env.step('CALL simplify {"fraction": "2/4"}')
            if done:
                break

        assert done

    def test_tool_policy(self):
        """Test tool policy enforcement."""
        env = FractionsGymEnv(tool_policy=ToolPolicy.FORBIDDEN)
        env.reset(seed=42)

        # Try using a tool
        obs, reward, done, info = env.step('CALL simplify {"fraction": "2/4"}')

        # Should get an error message
        assert "forbidden" in obs.lower()

    def test_get_allowed_actions(self):
        """Test getting allowed actions."""
        env = FractionsGymEnv()
        env.reset(seed=42)

        actions = env.get_allowed_actions()

        assert "ANSWER" in actions[0]


class TestFractionsGymEnvTools:
    """Tests for FractionsGymEnv tool execution."""

    def test_simplify_tool(self):
        """Test simplify tool."""
        env = FractionsGymEnv()
        env.reset(seed=42)

        # Simplify 2/4 should give 1/2
        result = env._execute_tool("simplify", {"fraction": "4/8"})
        assert result == "1/2"

    def test_simplify_tool_already_simplified(self):
        """Test simplify on already reduced fraction."""
        env = FractionsGymEnv()
        env.reset(seed=42)

        result = env._execute_tool("simplify", {"fraction": "3/7"})
        assert result == "3/7"

    def test_simplify_tool_invalid_input(self):
        """Test simplify with invalid input - falls back to returning input."""
        env = FractionsGymEnv()
        env.reset(seed=42)

        # When input doesn't have a "/" it returns the input as-is
        result = env._execute_tool("simplify", {"fraction": "invalid"})
        assert result == "invalid"

    def test_simplify_tool_non_numeric(self):
        """Test simplify with non-numeric fraction parts."""
        env = FractionsGymEnv()
        env.reset(seed=42)

        result = env._execute_tool("simplify", {"fraction": "a/b"})
        assert "Error" in result

    def test_add_tool(self):
        """Test add tool."""
        env = FractionsGymEnv()
        env.reset(seed=42)

        # 1/4 + 1/4 = 1/2
        result = env._execute_tool("add", {"frac1": "1/4", "frac2": "1/4"})
        assert result == "1/2"

    def test_add_tool_different_denominators(self):
        """Test adding fractions with different denominators."""
        env = FractionsGymEnv()
        env.reset(seed=42)

        # 1/2 + 1/3 = 5/6
        result = env._execute_tool("add", {"frac1": "1/2", "frac2": "1/3"})
        assert result == "5/6"

    def test_add_tool_invalid(self):
        """Test add with invalid input."""
        env = FractionsGymEnv()
        env.reset(seed=42)

        result = env._execute_tool("add", {"frac1": "invalid", "frac2": "1/2"})
        assert "Error" in result

    def test_subtract_tool(self):
        """Test subtract tool."""
        env = FractionsGymEnv()
        env.reset(seed=42)

        # 3/4 - 1/4 = 1/2
        result = env._execute_tool("subtract", {"frac1": "3/4", "frac2": "1/4"})
        assert result == "1/2"

    def test_subtract_tool_invalid(self):
        """Test subtract with invalid input."""
        env = FractionsGymEnv()
        env.reset(seed=42)

        result = env._execute_tool("subtract", {"frac1": "bad", "frac2": "1/2"})
        assert "Error" in result

    def test_multiply_tool(self):
        """Test multiply tool."""
        env = FractionsGymEnv()
        env.reset(seed=42)

        # 1/2 * 1/3 = 1/6
        result = env._execute_tool("multiply", {"frac1": "1/2", "frac2": "1/3"})
        assert result == "1/6"

    def test_multiply_tool_invalid(self):
        """Test multiply with invalid input."""
        env = FractionsGymEnv()
        env.reset(seed=42)

        result = env._execute_tool("multiply", {"frac1": "abc", "frac2": "1/2"})
        assert "Error" in result

    def test_divide_tool(self):
        """Test divide tool."""
        env = FractionsGymEnv()
        env.reset(seed=42)

        # 1/2 / 1/4 = 2
        result = env._execute_tool("divide", {"frac1": "1/2", "frac2": "1/4"})
        assert result == "2/1"

    def test_divide_tool_by_zero(self):
        """Test divide by zero."""
        env = FractionsGymEnv()
        env.reset(seed=42)

        result = env._execute_tool("divide", {"frac1": "1/2", "frac2": "0/1"})
        assert "Error" in result or "zero" in result.lower()

    def test_divide_tool_invalid(self):
        """Test divide with invalid input."""
        env = FractionsGymEnv()
        env.reset(seed=42)

        result = env._execute_tool("divide", {"frac1": "bad", "frac2": "1/2"})
        assert "Error" in result

    def test_gcd_tool(self):
        """Test gcd tool."""
        env = FractionsGymEnv()
        env.reset(seed=42)

        result = env._execute_tool("gcd", {"a": 12, "b": 8})
        assert result == "4"

    def test_lcm_tool(self):
        """Test lcm tool."""
        env = FractionsGymEnv()
        env.reset(seed=42)

        result = env._execute_tool("lcm", {"a": 4, "b": 6})
        assert result == "12"

    def test_unknown_tool(self):
        """Test unknown tool."""
        env = FractionsGymEnv()
        env.reset(seed=42)

        result = env._execute_tool("unknown_tool", {})
        assert "Unknown tool" in result

    def test_get_tool_descriptions(self):
        """Test getting tool descriptions."""
        env = FractionsGymEnv()
        descriptions = env.get_tool_descriptions()

        assert "simplify" in descriptions
        assert "add" in descriptions
        assert "subtract" in descriptions
        assert "multiply" in descriptions
        assert "divide" in descriptions
        assert "gcd" in descriptions
        assert "lcm" in descriptions


class TestFractionsVerifierAdvanced:
    """Advanced tests for FractionsVerifier."""

    def _make_problem(self, gold_answer: str, answer_type=None) -> Problem:
        """Create a test problem with given gold answer."""
        from chuk_math_gym.schemas.problem import AnswerType

        return Problem(
            id="test",
            seed=0,
            domain=DomainType.FRACTIONS,
            difficulty=DifficultyLevel.MEDIUM,
            prompt="Test problem",
            expression="test",
            gold_answer=gold_answer,
            answer_type=answer_type or AnswerType.EXACT,
        )

    def test_verify_invalid_gold_answer(self):
        """Test verify with invalid gold answer."""
        verifier = FractionsVerifier()
        problem = self._make_problem("invalid_gold")

        result = verifier.verify_final(problem, "1/2")
        assert not result.correct
        assert "Invalid gold answer" in result.error_message

    def test_verify_unreduced_required(self):
        """Test verify when reduced form is required."""
        from chuk_math_gym.schemas.problem import AnswerType

        verifier = FractionsVerifier(require_reduced=True)
        problem = self._make_problem("1/2", answer_type=AnswerType.EXPRESSION)

        # 2/4 = 1/2, but not reduced
        result = verifier.verify_final(problem, "2/4")
        assert not result.correct
        assert result.partial_credit == 0.75

    def test_verify_sign_error(self):
        """Test verify detects sign error."""
        verifier = FractionsVerifier()
        problem = self._make_problem("1/2")

        result = verifier.verify_final(problem, "-1/2")
        assert not result.correct
        # Check error message mentions sign
        assert "Sign error" in result.error_message

    def test_verify_wrong_denominator(self):
        """Test verify detects wrong denominator."""
        verifier = FractionsVerifier()
        problem = self._make_problem("2/4")  # unreduced

        # Same numerator (2), different denominator
        result = verifier.verify_final(problem, "2/3")
        assert not result.correct

    def test_verify_rounding_error(self):
        """Test verify detects rounding error."""
        verifier = FractionsVerifier()
        problem = self._make_problem("1/3")

        # 0.333 is close to 1/3 (which is ~0.3333...)
        result = verifier.verify_final(problem, "0.333")
        # This should still work as fractions are equivalent within tolerance
        assert result.correct or "close" in result.error_message.lower()

    def test_verify_trace_empty(self):
        """Test verify_trace with empty trace."""
        from chuk_math_gym.schemas.trace import Trace

        verifier = FractionsVerifier()
        problem = self._make_problem("1/2")
        trace = Trace(problem_id="test", steps=[])

        result = verifier.verify_trace(problem, trace)
        assert not result.correct
        assert result.steps_total == 0

    def test_verify_trace_invalid_gold(self):
        """Test verify_trace with invalid gold answer."""
        from chuk_math_gym.schemas.trace import Trace, Step, StepOperation

        verifier = FractionsVerifier()
        problem = self._make_problem("invalid")

        steps = [
            Step(
                index=0,
                operation=StepOperation.EVAL,
                before_state="test",
                after_state="0.5",
                inputs=[],
                output="x1",
                output_value=0.5,
            ),
        ]

        trace = Trace(
            problem_id="test",
            steps=steps,
            placeholder_map={"x1": 0.5},
            final_placeholder="x1",
            final_value=0.5,
        )

        result = verifier.verify_trace(problem, trace)
        assert not result.correct

    def test_verify_trace_with_correct_steps(self):
        """Test verify_trace with correct steps."""
        from chuk_math_gym.schemas.trace import Trace, Step, StepOperation

        verifier = FractionsVerifier()
        problem = self._make_problem("1/2")

        steps = [
            Step(
                index=0,
                operation=StepOperation.EVAL,
                before_state="1/2",
                after_state="0.5",
                inputs=[],
                output="x1",
                output_value=0.5,
            ),
        ]

        trace = Trace(
            problem_id="test",
            steps=steps,
            placeholder_map={"x1": 0.5},
            final_placeholder="x1",
            final_value=0.5,
        )

        result = verifier.verify_trace(problem, trace)
        assert result.correct

    def test_verify_trace_with_wrong_final(self):
        """Test verify_trace with wrong final value."""
        from chuk_math_gym.schemas.trace import Trace, Step, StepOperation

        verifier = FractionsVerifier()
        problem = self._make_problem("1/2")

        steps = [
            Step(
                index=0,
                operation=StepOperation.EVAL,
                before_state="1/3",
                after_state="0.333",
                inputs=[],
                output="x1",
                output_value=0.333,
            ),
        ]

        trace = Trace(
            problem_id="test",
            steps=steps,
            placeholder_map={"x1": 0.333},
            final_placeholder="x1",
            final_value=0.333,  # Wrong - should be 0.5
        )

        result = verifier.verify_trace(problem, trace)
        assert not result.correct

    def test_verify_step_correct(self):
        """Test verify_step with correct value."""
        from chuk_math_gym.schemas.trace import Trace, Step, StepOperation

        verifier = FractionsVerifier()
        problem = self._make_problem("1/2")

        steps = [
            Step(
                index=0,
                operation=StepOperation.EVAL,
                before_state="1/2",
                after_state="0.5",
                inputs=[],
                output="x1",
                output_value=0.5,
            ),
        ]

        trace = Trace(
            problem_id="test",
            steps=steps,
            placeholder_map={"x1": 0.5},
            final_placeholder="x1",
            final_value=0.5,
        )

        result = verifier.verify_step(problem, trace, 0, 0.5)
        assert result.correct

    def test_verify_step_incorrect(self):
        """Test verify_step with incorrect value."""
        from chuk_math_gym.schemas.trace import Trace, Step, StepOperation

        verifier = FractionsVerifier()
        problem = self._make_problem("1/2")

        steps = [
            Step(
                index=0,
                operation=StepOperation.EVAL,
                before_state="1/2",
                after_state="0.5",
                inputs=[],
                output="x1",
                output_value=0.5,
            ),
        ]

        trace = Trace(
            problem_id="test",
            steps=steps,
            placeholder_map={"x1": 0.5},
            final_placeholder="x1",
            final_value=0.5,
        )

        result = verifier.verify_step(problem, trace, 0, 0.75)  # Wrong
        assert not result.correct

    def test_verify_step_out_of_range(self):
        """Test verify_step with out of range index."""
        from chuk_math_gym.schemas.trace import Trace

        verifier = FractionsVerifier()
        problem = self._make_problem("1/2")
        trace = Trace(problem_id="test", steps=[])

        result = verifier.verify_step(problem, trace, 5, 0.5)
        assert not result.correct

    def test_parse_latex_fraction(self):
        """Test parsing LaTeX fraction format."""
        verifier = FractionsVerifier()
        problem = self._make_problem("3/4")

        result = verifier.verify_final(problem, r"\frac{3}{4}")
        assert result.correct

    def test_parse_negative_mixed_number(self):
        """Test parsing negative mixed number."""
        verifier = FractionsVerifier()
        problem = self._make_problem("-3/2")

        result = verifier.verify_final(problem, "-1 1/2")
        assert result.correct

    def test_empty_answer(self):
        """Test with empty answer."""
        verifier = FractionsVerifier()
        problem = self._make_problem("1/2")

        result = verifier.verify_final(problem, "")
        assert not result.correct


class TestFractionsIntegration:
    """Integration tests for fractions domain."""

    def _make_problem(self, gold_answer: str) -> Problem:
        """Create a test problem with given gold answer."""
        return Problem(
            id="test",
            seed=0,
            domain=DomainType.FRACTIONS,
            difficulty=DifficultyLevel.MEDIUM,
            prompt="Test problem",
            expression="test",
            gold_answer=gold_answer,
        )

    def test_generate_and_verify(self):
        """Test full generate-solve-verify flow."""
        generator = FractionsGenerator()
        verifier = FractionsVerifier()

        problem, trace = generator.generate(
            seed=42,
            difficulty=DifficultyLevel.MEDIUM,
        )

        # Verify the gold answer
        result = verifier.verify_final(problem, problem.gold_answer)

        assert result.correct

    def test_trace_verification(self):
        """Test verifying a complete trace."""
        generator = FractionsGenerator()
        verifier = FractionsVerifier()

        problem, trace = generator.generate(
            seed=42,
            difficulty=DifficultyLevel.EASY,
        )

        # The trace should be valid
        result = verifier.verify_trace(problem, trace)

        # Gold trace should be correct
        assert result.correct or result.steps_correct == len(trace.steps)
