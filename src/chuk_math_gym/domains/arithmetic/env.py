"""
Arithmetic Gym environment.

Implements the MathGymEnv interface for arithmetic problems.
"""

from typing import Optional

from chuk_math_gym.schemas.problem import (
    Problem,
    DifficultyLevel,
    ToolPolicy,
)
from chuk_math_gym.schemas.trace import Trace
from chuk_math_gym.verifiers.base import Verifier
from chuk_math_gym.verifiers.arithmetic import ArithmeticVerifier
from chuk_math_gym.env.base import MathGymEnv
from chuk_math_gym.domains.arithmetic.generator import ArithmeticGenerator


class ArithmeticGymEnv(MathGymEnv):
    """
    Gym environment for arithmetic problems.

    Supports three game modes:
    1. Mental math (tools forbidden) - agent must compute answer mentally
    2. Tool-assisted (tools allowed) - agent can use calculator tools
    3. Tool-required (tools required) - agent must use specific tools

    Example:
        env = ArithmeticGymEnv(tool_policy=ToolPolicy.ALLOWED)
        problem = env.reset(seed=42, difficulty=DifficultyLevel.MEDIUM)

        # Agent loop
        obs, reward, done, info = env.step("ANSWER 42")
        print(f"Correct: {info['verification_result']['correct']}")
    """

    def __init__(
        self,
        tool_policy: ToolPolicy = ToolPolicy.ALLOWED,
        max_steps: int = 10,
        step_penalty: float = -0.01,
        wrong_answer_penalty: float = -1.0,
        correct_reward: float = 1.0,
        efficiency_bonus: float = 0.1,
    ):
        """
        Initialize the arithmetic environment.

        Args:
            tool_policy: Default tool policy
            max_steps: Maximum steps per episode
            step_penalty: Small penalty per step
            wrong_answer_penalty: Penalty for wrong answer
            correct_reward: Reward for correct answer
            efficiency_bonus: Bonus for efficient solutions
        """
        super().__init__(
            tool_policy=tool_policy,
            max_steps=max_steps,
            step_penalty=step_penalty,
            wrong_answer_penalty=wrong_answer_penalty,
            correct_reward=correct_reward,
            efficiency_bonus=efficiency_bonus,
        )

        self._generator = ArithmeticGenerator()
        self._verifier = ArithmeticVerifier()

    def _generate_problem(
        self,
        seed: int,
        difficulty: DifficultyLevel,
    ) -> Problem:
        """Generate an arithmetic problem."""
        problem, _ = self._generator.generate(
            seed=seed,
            difficulty=difficulty,
            tool_policy=self.tool_policy,
        )
        return problem

    def _generate_trace(self, problem: Problem) -> Trace:
        """Generate the solution trace for a problem."""
        # Re-generate with same seed to get trace
        _, trace = self._generator.generate(
            seed=problem.seed,
            difficulty=problem.difficulty,
            tool_policy=problem.tool_policy,
        )
        return trace

    def _get_verifier(self) -> Verifier:
        """Get the arithmetic verifier."""
        return self._verifier

    def _execute_tool(self, tool_name: str, args: dict) -> str:
        """
        Execute a tool call.

        Supported tools:
        - calculate: Evaluate an arithmetic expression
        - add, subtract, multiply, divide: Basic operations
        """
        if tool_name == "calculate":
            expr = args.get("expression", "")
            try:
                result = self._generator._evaluate_expression(expr)
                return str(result)
            except Exception as e:
                return f"Error: {e}"

        elif tool_name == "add":
            a = float(args.get("a", 0))
            b = float(args.get("b", 0))
            return str(a + b)

        elif tool_name == "subtract":
            a = float(args.get("a", 0))
            b = float(args.get("b", 0))
            return str(a - b)

        elif tool_name == "multiply":
            a = float(args.get("a", 0))
            b = float(args.get("b", 0))
            return str(a * b)

        elif tool_name == "divide":
            a = float(args.get("a", 0))
            b = float(args.get("b", 1))
            if b == 0:
                return "Error: Division by zero"
            return str(a / b)

        else:
            return f"Unknown tool: {tool_name}"

    def get_tool_descriptions(self) -> dict[str, str]:
        """Get descriptions of available tools."""
        return {
            "calculate": "Evaluate an arithmetic expression. Args: {expression: str}",
            "add": "Add two numbers. Args: {a: float, b: float}",
            "subtract": "Subtract b from a. Args: {a: float, b: float}",
            "multiply": "Multiply two numbers. Args: {a: float, b: float}",
            "divide": "Divide a by b. Args: {a: float, b: float}",
        }


def create_mental_math_env(**kwargs) -> ArithmeticGymEnv:
    """Create an environment where tools are forbidden (mental math only)."""
    return ArithmeticGymEnv(tool_policy=ToolPolicy.FORBIDDEN, **kwargs)


def create_tool_assisted_env(**kwargs) -> ArithmeticGymEnv:
    """Create an environment where tools are allowed."""
    return ArithmeticGymEnv(tool_policy=ToolPolicy.ALLOWED, **kwargs)
