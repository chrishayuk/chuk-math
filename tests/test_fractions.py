"""Tests for the fractions domain."""

import pytest
from fractions import Fraction

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
            generator.generate(seed=i, difficulty=DifficultyLevel.VERY_EASY)[0]
            for i in range(10)
        ]

        hard_problems = [
            generator.generate(seed=i+100, difficulty=DifficultyLevel.VERY_HARD)[0]
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
        problem = env.reset(seed=42)

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
        problem = env.reset(seed=42)

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
