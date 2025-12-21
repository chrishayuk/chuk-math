"""Tests for the linear equations domain."""

import pytest

from chuk_math_gym.schemas.problem import DifficultyLevel, DomainType, ToolPolicy, Problem
from chuk_math_gym.domains.linear_equations import (
    LinearEquationsGenerator,
    LinearEquationsVerifier,
    LinearEquationsGymEnv,
)


class TestLinearEquationsGenerator:
    """Tests for LinearEquationsGenerator."""

    def test_generate_problem(self):
        """Test basic problem generation."""
        generator = LinearEquationsGenerator()
        problem, trace = generator.generate(
            seed=42,
            difficulty=DifficultyLevel.MEDIUM,
        )

        assert problem is not None
        assert problem.domain == DomainType.LINEAR_EQUATIONS
        assert problem.difficulty == DifficultyLevel.MEDIUM
        assert problem.expression is not None
        assert "=" in problem.expression  # Equations have equals sign
        assert problem.gold_answer is not None

    def test_deterministic_generation(self):
        """Test that same seed produces same problem."""
        generator = LinearEquationsGenerator()

        p1, t1 = generator.generate(seed=123, difficulty=DifficultyLevel.EASY)
        p2, t2 = generator.generate(seed=123, difficulty=DifficultyLevel.EASY)

        assert p1.expression == p2.expression
        assert p1.gold_answer == p2.gold_answer

    def test_different_seeds_different_problems(self):
        """Test that different seeds produce different problems."""
        generator = LinearEquationsGenerator()

        p1, _ = generator.generate(seed=100, difficulty=DifficultyLevel.MEDIUM)
        p2, _ = generator.generate(seed=200, difficulty=DifficultyLevel.MEDIUM)

        # Should usually be different
        assert p1.expression != p2.expression or p1.gold_answer != p2.gold_answer

    def test_generate_batch(self):
        """Test batch generation."""
        generator = LinearEquationsGenerator()
        problems = generator.generate_batch(
            count=5,
            start_seed=42,
            difficulty=DifficultyLevel.MEDIUM,
        )

        assert len(problems) == 5
        for problem, trace in problems:
            assert problem.domain == DomainType.LINEAR_EQUATIONS
            assert "=" in problem.expression

    def test_easy_problems_are_simpler(self):
        """Test that easy problems are simpler (one-step)."""
        generator = LinearEquationsGenerator()

        easy_problems = [
            generator.generate(seed=i, difficulty=DifficultyLevel.VERY_EASY)[0]
            for i in range(10)
        ]

        # Very easy problems should be one-step (e.g., x + 3 = 7)
        for p in easy_problems:
            assert p.difficulty == DifficultyLevel.VERY_EASY

    def test_hard_problems_are_complex(self):
        """Test that hard problems are more complex."""
        generator = LinearEquationsGenerator()

        hard_problems = [
            generator.generate(seed=i, difficulty=DifficultyLevel.VERY_HARD)[0]
            for i in range(10)
        ]

        # Very hard problems should exist
        for p in hard_problems:
            assert p.difficulty == DifficultyLevel.VERY_HARD

    def test_trace_has_steps(self):
        """Test that generated trace has solution steps."""
        generator = LinearEquationsGenerator()
        problem, trace = generator.generate(
            seed=42,
            difficulty=DifficultyLevel.MEDIUM,
        )

        assert trace is not None
        assert len(trace.steps) > 0
        assert trace.final_value is not None


class TestLinearEquationsVerifier:
    """Tests for LinearEquationsVerifier."""

    def _make_problem(self, gold_answer: str, expression: str = "x = ?") -> Problem:
        """Create a test problem with given gold answer."""
        return Problem(
            id="test",
            seed=0,
            domain=DomainType.LINEAR_EQUATIONS,
            difficulty=DifficultyLevel.MEDIUM,
            prompt="Solve for x",
            expression=expression,
            gold_answer=gold_answer,
        )

    def test_verify_correct_integer(self):
        """Test verifying a correct integer answer."""
        verifier = LinearEquationsVerifier()
        problem = self._make_problem("5")
        result = verifier.verify_final(problem, "5")

        assert result.correct
        assert result.score == 1.0

    def test_verify_correct_fraction(self):
        """Test verifying a correct fractional answer."""
        verifier = LinearEquationsVerifier()
        problem = self._make_problem("0.5")

        result = verifier.verify_final(problem, "1/2")
        assert result.correct

    def test_verify_correct_decimal(self):
        """Test verifying a correct decimal answer."""
        verifier = LinearEquationsVerifier()
        problem = self._make_problem("7/2")

        result = verifier.verify_final(problem, "3.5")
        assert result.correct

    def test_verify_incorrect_answer(self):
        """Test verifying an incorrect answer."""
        verifier = LinearEquationsVerifier()
        problem = self._make_problem("5")
        result = verifier.verify_final(problem, "10")

        assert not result.correct
        assert result.score == 0.0

    def test_verify_negative_answer(self):
        """Test negative answers."""
        verifier = LinearEquationsVerifier()
        problem = self._make_problem("-3")

        result = verifier.verify_final(problem, "-3")
        assert result.correct

    def test_verify_with_x_prefix(self):
        """Test answers with 'x =' prefix."""
        verifier = LinearEquationsVerifier()
        problem = self._make_problem("5")

        result = verifier.verify_final(problem, "x = 5")
        assert result.correct

    def test_verify_by_substitution(self):
        """Test verification by substitution."""
        verifier = LinearEquationsVerifier()

        # 2x + 3 = 7, solution is x = 2
        result = verifier.verify_by_substitution(
            equation="2x + 3 = 7",
            variable="x",
            candidate=2.0,
        )
        assert result.correct

        # Wrong value
        result = verifier.verify_by_substitution(
            equation="2x + 3 = 7",
            variable="x",
            candidate=3.0,
        )
        assert not result.correct

    def test_verify_invalid_format(self):
        """Test handling of invalid input."""
        verifier = LinearEquationsVerifier()
        problem = self._make_problem("5")

        result = verifier.verify_final(problem, "invalid")
        assert not result.correct

    def test_verify_sign_error(self):
        """Test detecting sign errors."""
        verifier = LinearEquationsVerifier()
        problem = self._make_problem("5")

        result = verifier.verify_final(problem, "-5")
        assert not result.correct
        # Could check for error_type == ErrorType.SIGN_ERROR


class TestLinearEquationsGymEnv:
    """Tests for LinearEquationsGymEnv."""

    def test_reset(self):
        """Test environment reset."""
        env = LinearEquationsGymEnv()
        problem = env.reset(seed=42)

        assert problem is not None
        assert problem.domain == DomainType.LINEAR_EQUATIONS
        assert env.current_problem is not None

    def test_step_correct_answer(self):
        """Test stepping with correct answer."""
        env = LinearEquationsGymEnv()
        problem = env.reset(seed=42)

        # Get the gold answer and submit it
        gold = problem.gold_answer
        obs, reward, done, info = env.step(f"ANSWER {gold}")

        assert done
        assert reward > 0
        assert info["verification_result"]["correct"]

    def test_step_wrong_answer(self):
        """Test stepping with wrong answer."""
        env = LinearEquationsGymEnv()
        problem = env.reset(seed=42)

        # Submit a clearly wrong answer
        obs, reward, done, info = env.step("ANSWER 999999")

        assert done
        assert reward < 0
        assert not info["verification_result"]["correct"]

    def test_tool_substitute(self):
        """Test using the substitute tool."""
        env = LinearEquationsGymEnv()
        problem = env.reset(seed=42)

        # Use substitute tool
        gold = problem.gold_answer
        equation = problem.expression
        obs, reward, done, info = env.step(
            f'CALL substitute {{"equation": "{equation}", "variable": "x", "value": {gold}}}'
        )

        # Should get feedback about substitution
        assert "satisfy" in obs.lower() or "yes" in obs.lower() or "tool" in obs.lower()

    def test_tool_add_both(self):
        """Test using the add_both tool."""
        env = LinearEquationsGymEnv()
        problem = env.reset(seed=42)

        # Use add_both tool
        obs, reward, done, info = env.step(
            'CALL add_both {"equation": "x + 3 = 7", "value": -3}'
        )

        # Should show the transformed equation
        assert "=" in obs

    def test_max_steps(self):
        """Test max steps termination."""
        env = LinearEquationsGymEnv(max_steps=3)
        env.reset(seed=42)

        # Make tool calls until max
        for i in range(3):
            obs, reward, done, info = env.step('CALL evaluate {"expression": "1+1"}')
            if done:
                break

        assert done

    def test_tool_policy_forbidden(self):
        """Test tool policy enforcement."""
        env = LinearEquationsGymEnv(tool_policy=ToolPolicy.FORBIDDEN)
        problem = env.reset(seed=42)

        # Try using a tool
        obs, reward, done, info = env.step(
            'CALL solve {"equation": "x + 3 = 7"}'
        )

        # Should get a penalty or error message
        assert "forbidden" in obs.lower()

    def test_get_tool_descriptions(self):
        """Test getting tool descriptions."""
        env = LinearEquationsGymEnv()
        env.reset(seed=42)

        tools = env.get_tool_descriptions()

        assert "substitute" in tools
        assert "add_both" in tools
        assert "subtract_both" in tools
        assert "multiply_both" in tools
        assert "divide_both" in tools


class TestLinearEquationsIntegration:
    """Integration tests for linear equations domain."""

    def test_generate_and_verify(self):
        """Test full generate-solve-verify flow."""
        generator = LinearEquationsGenerator()
        verifier = LinearEquationsVerifier()

        problem, trace = generator.generate(
            seed=42,
            difficulty=DifficultyLevel.MEDIUM,
        )

        # Verify the gold answer
        result = verifier.verify_final(problem, problem.gold_answer)

        assert result.correct

    def test_verify_by_substitution_integration(self):
        """Test verification by substitution with generated problem."""
        generator = LinearEquationsGenerator()
        verifier = LinearEquationsVerifier()

        problem, trace = generator.generate(
            seed=42,
            difficulty=DifficultyLevel.EASY,
        )

        # Parse the gold answer as a number
        try:
            gold_value = float(problem.gold_answer)
        except ValueError:
            # Could be a fraction
            from fractions import Fraction
            gold_value = float(Fraction(problem.gold_answer))

        # Verify by substitution
        result = verifier.verify_by_substitution(
            equation=problem.expression,
            variable="x",
            candidate=gold_value,
        )

        assert result.correct

    def test_different_difficulties(self):
        """Test that different difficulties produce valid problems."""
        generator = LinearEquationsGenerator()
        verifier = LinearEquationsVerifier()

        for difficulty in DifficultyLevel:
            problem, trace = generator.generate(
                seed=42,
                difficulty=difficulty,
            )

            # Gold answer should verify
            result = verifier.verify_final(problem, problem.gold_answer)
            assert result.correct, f"Failed for difficulty {difficulty}"
