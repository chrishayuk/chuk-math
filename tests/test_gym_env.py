"""Tests for chuk-math-gym environments."""

import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from chuk_math_gym.schemas.problem import DifficultyLevel, ToolPolicy
from chuk_math_gym.domains.arithmetic import ArithmeticGymEnv, ArithmeticGenerator


class TestArithmeticGenerator:
    """Tests for the ArithmeticGenerator."""

    @pytest.fixture
    def generator(self):
        return ArithmeticGenerator()

    def test_generate_problem(self, generator):
        """Test generating a problem."""
        problem, trace = generator.generate(
            seed=42,
            difficulty=DifficultyLevel.EASY,
        )

        assert problem.id == "arithmetic_easy_42"
        assert problem.seed == 42
        assert problem.difficulty == DifficultyLevel.EASY
        assert problem.prompt is not None
        assert problem.gold_answer is not None
        assert trace.problem_id == problem.id
        assert trace.final_value is not None

    def test_deterministic_generation(self, generator):
        """Test that same seed produces same problem."""
        problem1, trace1 = generator.generate(seed=42, difficulty=DifficultyLevel.MEDIUM)
        problem2, trace2 = generator.generate(seed=42, difficulty=DifficultyLevel.MEDIUM)

        assert problem1.expression == problem2.expression
        assert problem1.gold_answer == problem2.gold_answer
        assert trace1.final_value == trace2.final_value

    def test_different_seeds_different_problems(self, generator):
        """Test that different seeds produce different problems."""
        problem1, _ = generator.generate(seed=42, difficulty=DifficultyLevel.MEDIUM)
        problem2, _ = generator.generate(seed=43, difficulty=DifficultyLevel.MEDIUM)

        # Very unlikely to be the same
        assert problem1.expression != problem2.expression or problem1.gold_answer != problem2.gold_answer

    def test_generate_batch(self, generator):
        """Test batch generation."""
        batch = generator.generate_batch(
            count=5,
            difficulty=DifficultyLevel.EASY,
            start_seed=100,
        )

        assert len(batch) == 5

        # Check all have different IDs
        ids = [p.id for p, _ in batch]
        assert len(set(ids)) == 5

    def test_difficulty_affects_expression(self, generator):
        """Test that difficulty affects expression complexity."""
        easy_problem, _ = generator.generate(seed=42, difficulty=DifficultyLevel.VERY_EASY)
        hard_problem, _ = generator.generate(seed=42, difficulty=DifficultyLevel.VERY_HARD)

        # Hard problems should generally have more operations or larger numbers
        # This is a soft check - just verify they're different
        assert easy_problem.expression != hard_problem.expression


class TestArithmeticGymEnv:
    """Tests for the ArithmeticGymEnv."""

    @pytest.fixture
    def env(self):
        return ArithmeticGymEnv()

    def test_reset(self, env):
        """Test environment reset."""
        problem = env.reset(seed=42, difficulty=DifficultyLevel.EASY)

        assert problem is not None
        assert problem.seed == 42
        assert problem.difficulty == DifficultyLevel.EASY
        assert env.state is not None
        assert not env.state.done

    def test_step_correct_answer(self, env):
        """Test stepping with correct answer."""
        problem = env.reset(seed=42, difficulty=DifficultyLevel.EASY)

        # Get the gold answer
        gold = problem.gold_answer

        obs, reward, done, info = env.step(f"ANSWER {gold}")

        assert done
        assert info["verification_result"]["correct"]
        assert reward > 0  # Should get positive reward

    def test_step_wrong_answer(self, env):
        """Test stepping with wrong answer."""
        problem = env.reset(seed=42, difficulty=DifficultyLevel.EASY)

        obs, reward, done, info = env.step("ANSWER 999999")

        assert done
        assert not info["verification_result"]["correct"]
        assert reward < 0  # Should get negative reward

    def test_step_direct_answer(self, env):
        """Test stepping with just the answer (no ANSWER prefix)."""
        problem = env.reset(seed=42, difficulty=DifficultyLevel.EASY)
        gold = problem.gold_answer

        # Should work without "ANSWER" prefix
        obs, reward, done, info = env.step(gold)

        assert done
        assert info["verification_result"]["correct"]

    def test_tool_call(self, env):
        """Test making a tool call."""
        problem = env.reset(seed=42, difficulty=DifficultyLevel.MEDIUM)

        obs, reward, done, info = env.step('CALL calculate {"expression": "2 + 2"}')

        assert not done  # Episode continues
        assert "4" in obs  # Tool result should contain answer
        assert info.get("tool_result") is not None

    def test_tool_forbidden(self):
        """Test that tools are blocked when forbidden."""
        env = ArithmeticGymEnv(tool_policy=ToolPolicy.FORBIDDEN)
        problem = env.reset(seed=42)

        obs, reward, done, info = env.step('CALL calculate {"expression": "2 + 2"}')

        assert not done
        assert "forbidden" in obs.lower()
        assert info.get("error") == "tool_forbidden"

    def test_max_steps(self):
        """Test max steps limit."""
        env = ArithmeticGymEnv(max_steps=3)
        problem = env.reset(seed=42)

        # Make tool calls until max steps
        for _ in range(3):
            obs, reward, done, info = env.step('CALL calculate {"expression": "1 + 1"}')

        assert done
        assert info.get("error") == "max_steps"

    def test_render(self, env):
        """Test rendering state."""
        problem = env.reset(seed=42, difficulty=DifficultyLevel.EASY)

        output = env.render()

        assert "Problem:" in output
        assert "Difficulty:" in output
        assert "easy" in output.lower()

    def test_get_allowed_actions(self, env):
        """Test getting allowed actions."""
        env.reset(seed=42)

        actions = env.get_allowed_actions()

        assert "ANSWER <value>" in actions
        assert "CALL <tool_name> <args>" in actions

    def test_get_allowed_actions_forbidden(self):
        """Test allowed actions when tools forbidden."""
        env = ArithmeticGymEnv(tool_policy=ToolPolicy.FORBIDDEN)
        env.reset(seed=42)

        actions = env.get_allowed_actions()

        assert "ANSWER <value>" in actions
        assert "CALL <tool_name> <args>" not in actions

    def test_episode_tracking(self, env):
        """Test episode state tracking."""
        problem = env.reset(seed=42)

        assert env.state.steps_taken == 0
        assert env.state.tool_calls == []

        env.step('CALL calculate {"expression": "2 + 2"}')

        assert env.state.steps_taken == 1
        assert len(env.state.tool_calls) == 1

        env.step("ANSWER 4")

        assert env.state.done
        assert env.state.final_result is not None

    def test_current_problem_property(self, env):
        """Test current_problem property."""
        assert env.current_problem is None

        problem = env.reset(seed=42)

        assert env.current_problem == problem

    def test_efficiency_bonus(self):
        """Test efficiency bonus for quick solutions."""
        env = ArithmeticGymEnv(efficiency_bonus=0.5)
        problem = env.reset(seed=42)
        gold = problem.gold_answer

        # Answer immediately (1 step)
        obs, reward, done, info = env.step(f"ANSWER {gold}")

        # Should get base reward + efficiency bonus
        assert reward > env.correct_reward  # Has bonus


class TestEnvironmentModes:
    """Test different environment configurations."""

    def test_mental_math_mode(self):
        """Test mental math mode (no tools)."""
        from chuk_math_gym.domains.arithmetic.env import create_mental_math_env

        env = create_mental_math_env()
        problem = env.reset(seed=42)

        assert problem.tool_policy == ToolPolicy.FORBIDDEN

    def test_tool_assisted_mode(self):
        """Test tool-assisted mode."""
        from chuk_math_gym.domains.arithmetic.env import create_tool_assisted_env

        env = create_tool_assisted_env()
        problem = env.reset(seed=42)

        assert problem.tool_policy == ToolPolicy.ALLOWED


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
