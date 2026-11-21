"""
Arithmetic Gym environment.

Implements the MathGymEnv interface for arithmetic problems.
"""

from typing import Any

from chuk_gym_core import DifficultyLevel, ToolPolicy

from chuk_math_gym.schemas.problem import Problem
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
        obs, info = await env.reset(seed=42, difficulty=DifficultyLevel.MEDIUM)

        # Agent loop
        obs, reward, terminated, truncated, info = await env.step("ANSWER 42")
        print(f"Correct: {info.get('success')}")
    """

    def __init__(
        self,
        tool_policy: ToolPolicy = ToolPolicy.ALLOWED,
        max_steps: int = 10,
        step_penalty: float = -0.01,
        invalid_penalty: float = -0.1,
        hint_penalty: float = -0.1,
        correct_reward: float = 1.0,
        completion_bonus: float = 1.0,
        efficiency_multiplier: float = 0.1,
    ):
        """
        Initialize the arithmetic environment.

        Args:
            tool_policy: Default tool policy
            max_steps: Maximum steps per episode
            step_penalty: Small penalty per step
            invalid_penalty: Penalty for invalid actions
            hint_penalty: Penalty for using hints
            correct_reward: Reward for correct answer
            completion_bonus: Bonus for completing problem
            efficiency_multiplier: Multiplier for efficiency bonus
        """
        super().__init__(
            tool_policy=tool_policy,
            max_steps=max_steps,
            step_penalty=step_penalty,
            invalid_penalty=invalid_penalty,
            hint_penalty=hint_penalty,
            correct_reward=correct_reward,
            completion_bonus=completion_bonus,
            efficiency_multiplier=efficiency_multiplier,
        )

        self._generator = ArithmeticGenerator()
        self._arith_verifier = ArithmeticVerifier()

    @property
    def domain(self) -> str:
        """Domain identifier."""
        return "arithmetic"

    async def _generate_problem(
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

    async def _generate_trace(self, problem: Problem) -> Trace | None:
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
        return self._arith_verifier

    async def _execute_tool(self, tool_name: str, args: dict[str, Any]) -> str:
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
