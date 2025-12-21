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

    def test_generate_auto_seed(self, generator):
        """Test generation without specifying seed."""
        problem, trace = generator.generate(difficulty=DifficultyLevel.EASY)

        assert problem.seed is not None
        assert problem.seed >= 0
        assert trace.problem_id == problem.id

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
        assert (
            problem1.expression != problem2.expression
            or problem1.gold_answer != problem2.gold_answer
        )

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

    def test_generate_batch_auto_seed(self, generator):
        """Test batch generation without start_seed."""
        batch = generator.generate_batch(count=3, difficulty=DifficultyLevel.EASY)

        assert len(batch) == 3
        # Each should have unique IDs
        ids = [p.id for p, _ in batch]
        assert len(set(ids)) == 3

    def test_all_difficulty_levels(self, generator):
        """Test generation at all difficulty levels."""
        for level in DifficultyLevel:
            problem, trace = generator.generate(seed=42, difficulty=level)
            assert problem.difficulty == level
            assert trace.final_value is not None

    def test_pretty_easy_with_negatives(self, generator):
        """Test pretty easy difficulty allows negatives."""
        problem, _ = generator.generate(seed=42, difficulty=DifficultyLevel.PRETTY_EASY)
        assert problem.has_negatives

    def test_hard_with_decimals(self, generator):
        """Test hard difficulty allows decimals."""
        problem, _ = generator.generate(seed=42, difficulty=DifficultyLevel.HARD)
        assert problem.has_decimals

    def test_common_mistakes_order_of_operations(self, generator):
        """Test common mistakes detection for order of operations."""
        from chuk_math_gym.domains.arithmetic.generator import ArithmeticGenerator

        gen = ArithmeticGenerator()
        mistakes = gen._get_common_mistakes("3 + 5 * 2")
        assert "order_of_operations" in mistakes

    def test_common_mistakes_sign_error(self, generator):
        """Test common mistakes detection for sign errors."""
        from chuk_math_gym.domains.arithmetic.generator import ArithmeticGenerator

        gen = ArithmeticGenerator()
        mistakes = gen._get_common_mistakes("5 - 3")
        assert "sign_error" in mistakes

    def test_common_mistakes_division(self, generator):
        """Test common mistakes detection for division."""
        from chuk_math_gym.domains.arithmetic.generator import ArithmeticGenerator

        gen = ArithmeticGenerator()
        mistakes = gen._get_common_mistakes("10 / 2")
        assert "division_error" in mistakes

    def test_simple_expression_generator(self, generator):
        """Test the simple expression fallback generator."""
        from chuk_math_gym.domains.arithmetic.generator import DIFFICULTY_CONFIG, DifficultyLevel

        config = DIFFICULTY_CONFIG[DifficultyLevel.PRETTY_EASY]
        expr = generator._simple_expression(config)

        # Should be a valid expression
        assert isinstance(expr, str)
        assert len(expr) > 0
        # Should contain operators
        assert any(op in expr for op in "+-*/")

    def test_simple_expression_no_division(self, generator):
        """Test simple expression without division."""
        config = {
            "base_operands": 2,
            "min_number": 1,
            "max_number": 10,
            "allow_negative": False,
            "allow_division": False,
        }
        expr = generator._simple_expression(config)

        # Should not contain division
        assert "/" not in expr

    def test_safe_ast_eval_basic(self, generator):
        """Test safe AST evaluation."""
        result = generator._safe_ast_eval("2 + 3")
        assert result == 5.0

    def test_safe_ast_eval_complex(self, generator):
        """Test safe AST evaluation with complex expression."""
        result = generator._safe_ast_eval("(2 + 3) * 4 - 1")
        assert result == 19.0

    def test_safe_ast_eval_unary_negative(self, generator):
        """Test safe AST evaluation with unary negative."""
        result = generator._safe_ast_eval("-5 + 3")
        assert result == -2.0

    def test_safe_ast_eval_unary_positive(self, generator):
        """Test safe AST evaluation with unary positive."""
        result = generator._safe_ast_eval("+5 + 3")
        assert result == 8.0

    def test_safe_ast_eval_power(self, generator):
        """Test safe AST evaluation with power."""
        result = generator._safe_ast_eval("2 ** 3")
        assert result == 8.0

    def test_safe_ast_eval_invalid_constant(self, generator):
        """Test safe AST evaluation with invalid constant."""
        import pytest

        with pytest.raises(ValueError, match="Invalid constant"):
            generator._safe_ast_eval("'hello'")

    def test_safe_ast_eval_unsupported(self, generator):
        """Test safe AST evaluation with unsupported expression."""
        import pytest

        with pytest.raises(ValueError, match="Unsupported"):
            generator._safe_ast_eval("[1, 2, 3]")

    def test_evaluate_expression_sympy(self, generator):
        """Test expression evaluation with sympy."""
        result = generator._evaluate_expression("2 + 3 * 4")
        assert result == 14.0

    def test_evaluate_expression_fallback(self, generator):
        """Test expression evaluation fallback to AST."""
        # Force sympy to fail by using something it can't handle
        result = generator._evaluate_expression("(2 + 3)")
        assert result == 5.0

    def test_simple_expression_avoids_division_by_zero(self, generator):
        """Test that simple_expression avoids division by zero."""
        # Run several times to increase chance of hitting division path
        config = {
            "base_operands": 3,
            "min_number": 0,
            "max_number": 0,  # Force zeros
            "allow_negative": False,
            "allow_division": True,
        }
        # Seed to get consistent results
        import random

        random.seed(12345)
        generator._rng.seed(12345)

        # Generate expressions - division by zero should be avoided
        for _ in range(5):
            expr = generator._simple_expression(config)
            # Should not crash, and expression should be evaluable if it has division
            assert isinstance(expr, str)

    def test_generate_max_retries_exceeded(self, generator):
        """Test that RuntimeError is raised after max retries."""
        from unittest.mock import patch

        # Mock _evaluate_expression to always raise an exception
        with patch.object(generator, "_evaluate_expression", side_effect=ValueError("Test error")):
            with pytest.raises(RuntimeError, match="Failed to generate valid expression"):
                generator.generate(seed=42, difficulty=DifficultyLevel.EASY, _retry_count=10)

    def test_generate_retry_on_evaluation_failure(self, generator):
        """Test that generation retries when evaluation fails."""
        from unittest.mock import patch

        call_count = [0]
        original_evaluate = generator._evaluate_expression

        def failing_then_succeeding(expr):
            call_count[0] += 1
            if call_count[0] == 1:
                raise ValueError("Test error")
            return original_evaluate(expr)

        with patch.object(generator, "_evaluate_expression", side_effect=failing_then_succeeding):
            # Should retry and succeed
            problem, trace = generator.generate(seed=42, difficulty=DifficultyLevel.EASY)
            assert problem is not None
            assert call_count[0] == 2  # First call failed, second succeeded


class TestMathGymEnvBase:
    """Tests for MathGymEnv base class functionality."""

    @pytest.fixture
    def env(self):
        return ArithmeticGymEnv()

    def test_step_without_reset(self, env):
        """Test step raises error when called without reset."""
        with pytest.raises(RuntimeError, match="Must call reset"):
            env.step("ANSWER 5")

    def test_step_after_done(self, env):
        """Test step raises error when episode is done."""
        env.reset(seed=42)
        # Submit answer to end episode
        env.step("ANSWER 999")
        # Try to step again
        with pytest.raises(RuntimeError, match="Episode is done"):
            env.step("ANSWER 5")

    def test_reset_random_seed(self, env):
        """Test reset with random seed."""
        problem = env.reset()  # No seed specified
        assert problem is not None
        assert problem.seed >= 0

    def test_reset_random_difficulty(self, env):
        """Test reset with random difficulty."""
        problem = env.reset(seed=42)  # No difficulty specified
        assert problem is not None
        assert problem.difficulty in list(DifficultyLevel)

    def test_reset_with_tool_policy_override(self, env):
        """Test reset with tool policy override."""
        problem = env.reset(seed=42, tool_policy=ToolPolicy.FORBIDDEN)
        assert problem.tool_policy == ToolPolicy.FORBIDDEN

    def test_invalid_answer_format(self, env):
        """Test handling of invalid answer format (ANSWER without value)."""
        env.reset(seed=42)
        obs, reward, done, info = env.step("ANSWER")  # No value
        assert "Invalid answer format" in obs
        assert not done

    def test_invalid_tool_call_format(self, env):
        """Test handling of invalid tool call format."""
        env.reset(seed=42)
        obs, reward, done, info = env.step("CALL")  # No tool name
        assert "Invalid tool call format" in obs
        assert not done

    def test_tool_call_json_fallback(self, env):
        """Test tool call with non-JSON args falls back to simple value."""
        env.reset(seed=42)
        obs, reward, done, info = env.step("CALL calculate not_json")
        # Should not crash - uses args as simple value
        assert "Tool result" in obs

    def test_tool_policy_forbidden_on_answer(self, env):
        """Test tool policy violation detected on answer submission."""
        env2 = ArithmeticGymEnv(tool_policy=ToolPolicy.FORBIDDEN)
        env2.reset(seed=42)
        # First, try a tool call - it should be blocked
        obs, reward, done, info = env2.step('CALL calculate {"expression": "2+2"}')
        assert "forbidden" in obs.lower()

    def test_render_no_state(self, env):
        """Test render when no episode is active."""
        result = env.render()
        assert "No active episode" in result

    def test_render_active_episode(self, env):
        """Test render during active episode."""
        env.reset(seed=42)
        result = env.render()
        assert "Problem:" in result
        assert "Difficulty:" in result

    def test_render_after_done(self, env):
        """Test render after episode is done."""
        env.reset(seed=42)
        env.step("ANSWER 999")  # Wrong answer to end episode
        result = env.render()
        assert "Episode done" in result

    def test_current_trace_property(self, env):
        """Test current_trace property."""
        assert env.current_trace is None
        env.reset(seed=42)
        assert env.current_trace is not None

    def test_direct_answer_without_prefix(self, env):
        """Test submitting answer without ANSWER prefix."""
        env.reset(seed=42)
        gold = env.current_problem.gold_answer
        obs, reward, done, info = env.step(gold)  # Direct answer
        assert done

    def test_default_tool_execution(self):
        """Test default _execute_tool implementation."""
        from chuk_math_gym.env.base import MathGymEnv
        from chuk_math_gym.schemas.problem import Problem, DomainType
        from chuk_math_gym.schemas.trace import Trace

        class MinimalEnv(MathGymEnv):
            def _generate_problem(self, seed, difficulty):
                return Problem(
                    id="test",
                    seed=seed,
                    domain=DomainType.ARITHMETIC,
                    difficulty=difficulty,
                    prompt="Test",
                    gold_answer="5",
                )

            def _generate_trace(self, problem):
                return Trace(problem_id="test", steps=[], final_value=5.0)

            def _get_verifier(self):
                from chuk_math_gym.verifiers.arithmetic import ArithmeticVerifier

                return ArithmeticVerifier()

        env = MinimalEnv()
        env.reset(seed=42)
        result = env._execute_tool("test_tool", {"arg": "value"})
        assert "test_tool" in result
        assert "executed" in result


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
        env.reset(seed=42, difficulty=DifficultyLevel.EASY)

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
        env.reset(seed=42, difficulty=DifficultyLevel.MEDIUM)

        obs, reward, done, info = env.step('CALL calculate {"expression": "2 + 2"}')

        assert not done  # Episode continues
        assert "4" in obs  # Tool result should contain answer
        assert info.get("tool_result") is not None

    def test_tool_forbidden(self):
        """Test that tools are blocked when forbidden."""
        env = ArithmeticGymEnv(tool_policy=ToolPolicy.FORBIDDEN)
        env.reset(seed=42)

        obs, reward, done, info = env.step('CALL calculate {"expression": "2 + 2"}')

        assert not done
        assert "forbidden" in obs.lower()
        assert info.get("error") == "tool_forbidden"

    def test_max_steps(self):
        """Test max steps limit."""
        env = ArithmeticGymEnv(max_steps=3)
        env.reset(seed=42)

        # Make tool calls until max steps
        for _ in range(3):
            obs, reward, done, info = env.step('CALL calculate {"expression": "1 + 1"}')

        assert done
        assert info.get("error") == "max_steps"

    def test_render(self, env):
        """Test rendering state."""
        env.reset(seed=42, difficulty=DifficultyLevel.EASY)

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
        env.reset(seed=42)

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


class TestArithmeticGymEnvTools:
    """Tests for ArithmeticGymEnv tool execution."""

    @pytest.fixture
    def env(self):
        return ArithmeticGymEnv()

    def test_calculate_tool(self, env):
        """Test calculate tool."""
        env.reset(seed=42)

        result = env._execute_tool("calculate", {"expression": "2 + 3 * 4"})
        assert float(result) == 14.0

    def test_calculate_tool_error(self, env):
        """Test calculate tool with error."""
        env.reset(seed=42)

        result = env._execute_tool("calculate", {"expression": "invalid"})
        assert "Error" in result

    def test_add_tool(self, env):
        """Test add tool."""
        env.reset(seed=42)

        result = env._execute_tool("add", {"a": 3, "b": 5})
        assert float(result) == 8.0

    def test_subtract_tool(self, env):
        """Test subtract tool."""
        env.reset(seed=42)

        result = env._execute_tool("subtract", {"a": 10, "b": 3})
        assert float(result) == 7.0

    def test_multiply_tool(self, env):
        """Test multiply tool."""
        env.reset(seed=42)

        result = env._execute_tool("multiply", {"a": 4, "b": 5})
        assert float(result) == 20.0

    def test_divide_tool(self, env):
        """Test divide tool."""
        env.reset(seed=42)

        result = env._execute_tool("divide", {"a": 20, "b": 4})
        assert float(result) == 5.0

    def test_divide_by_zero(self, env):
        """Test divide by zero."""
        env.reset(seed=42)

        result = env._execute_tool("divide", {"a": 10, "b": 0})
        assert "Error" in result or "zero" in result.lower()

    def test_unknown_tool(self, env):
        """Test unknown tool."""
        env.reset(seed=42)

        result = env._execute_tool("unknown_tool", {})
        assert "Unknown tool" in result

    def test_get_tool_descriptions(self, env):
        """Test getting tool descriptions."""
        descriptions = env.get_tool_descriptions()

        assert "calculate" in descriptions
        assert "add" in descriptions
        assert "subtract" in descriptions
        assert "multiply" in descriptions
        assert "divide" in descriptions


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
