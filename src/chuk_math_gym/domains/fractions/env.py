"""
Fractions Gym environment.

Implements the MathGymEnv interface for fraction problems.
"""

from typing import Any

from chuk_gym_core import DifficultyLevel, ToolPolicy

from chuk_math_gym.schemas.problem import Problem
from chuk_math_gym.schemas.trace import Trace
from chuk_math_gym.verifiers.base import Verifier
from chuk_math_gym.env.base import MathGymEnv
from chuk_math_gym.domains.fractions.generator import FractionsGenerator
from chuk_math_gym.domains.fractions.verifier import FractionsVerifier


class FractionsGymEnv(MathGymEnv):
    """
    Gym environment for fraction problems.

    Supports various fraction operations:
    - Simplification
    - Addition/Subtraction
    - Multiplication/Division

    Example:
        env = FractionsGymEnv()
        obs, info = await env.reset(seed=42, difficulty=DifficultyLevel.MEDIUM)

        obs, reward, terminated, truncated, info = await env.step("ANSWER 1/2")
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
        require_reduced: bool = True,
    ):
        """
        Initialize the fractions environment.

        Args:
            tool_policy: Default tool policy
            max_steps: Maximum steps per episode
            step_penalty: Small penalty per step
            invalid_penalty: Penalty for invalid actions
            hint_penalty: Penalty for using hints
            correct_reward: Reward for correct answer
            completion_bonus: Bonus for completing problem
            efficiency_multiplier: Multiplier for efficiency bonus
            require_reduced: Whether answers must be in reduced form
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

        self._generator = FractionsGenerator()
        self._frac_verifier = FractionsVerifier(require_reduced=require_reduced)

    @property
    def domain(self) -> str:
        """Domain identifier."""
        return "fractions"

    async def _generate_problem(
        self,
        seed: int,
        difficulty: DifficultyLevel,
    ) -> Problem:
        """Generate a fraction problem."""
        problem, _ = self._generator.generate(
            seed=seed,
            difficulty=difficulty,
            tool_policy=self.tool_policy,
        )
        return problem

    async def _generate_trace(self, problem: Problem) -> Trace | None:
        """Generate the solution trace for a problem."""
        _, trace = self._generator.generate(
            seed=problem.seed,
            difficulty=problem.difficulty,
            tool_policy=problem.tool_policy,
        )
        return trace

    def _get_verifier(self) -> Verifier:
        """Get the fractions verifier."""
        return self._frac_verifier

    async def _execute_tool(self, tool_name: str, args: dict[str, Any]) -> str:
        """
        Execute a tool call.

        Supported tools:
        - simplify: Reduce a fraction to lowest terms
        - add: Add two fractions
        - subtract: Subtract fractions
        - multiply: Multiply fractions
        - divide: Divide fractions
        - gcd: Find greatest common divisor
        - lcm: Find least common multiple
        """
        import math
        from fractions import Fraction

        if tool_name == "simplify":
            frac = args.get("fraction", "1/1")
            try:
                parts = frac.split("/")
                if len(parts) == 2:
                    num, den = int(parts[0]), int(parts[1])
                    g = math.gcd(abs(num), abs(den))
                    return f"{num // g}/{den // g}"
                return str(frac)
            except Exception as e:
                return f"Error: {e}"

        elif tool_name == "add":
            f1 = args.get("frac1", "0/1")
            f2 = args.get("frac2", "0/1")
            try:
                pf1 = Fraction(f1)
                pf2 = Fraction(f2)
                result = pf1 + pf2
                return f"{result.numerator}/{result.denominator}"
            except Exception as e:
                return f"Error: {e}"

        elif tool_name == "subtract":
            f1 = args.get("frac1", "0/1")
            f2 = args.get("frac2", "0/1")
            try:
                pf1 = Fraction(f1)
                pf2 = Fraction(f2)
                result = pf1 - pf2
                return f"{result.numerator}/{result.denominator}"
            except Exception as e:
                return f"Error: {e}"

        elif tool_name == "multiply":
            f1 = args.get("frac1", "0/1")
            f2 = args.get("frac2", "0/1")
            try:
                pf1 = Fraction(f1)
                pf2 = Fraction(f2)
                result = pf1 * pf2
                return f"{result.numerator}/{result.denominator}"
            except Exception as e:
                return f"Error: {e}"

        elif tool_name == "divide":
            f1 = args.get("frac1", "0/1")
            f2 = args.get("frac2", "1/1")
            try:
                pf1 = Fraction(f1)
                pf2 = Fraction(f2)
                if pf2 == 0:
                    return "Error: Division by zero"
                result = pf1 / pf2
                return f"{result.numerator}/{result.denominator}"
            except Exception as e:
                return f"Error: {e}"

        elif tool_name == "gcd":
            a = int(args.get("a", 0))
            b = int(args.get("b", 0))
            return str(math.gcd(a, b))

        elif tool_name == "lcm":
            a = int(args.get("a", 1))
            b = int(args.get("b", 1))
            return str((a * b) // math.gcd(a, b))

        else:
            return f"Unknown tool: {tool_name}"

    def get_tool_descriptions(self) -> dict[str, str]:
        """Get descriptions of available tools."""
        return {
            "simplify": "Reduce a fraction to lowest terms. Args: {fraction: str}",
            "add": "Add two fractions. Args: {frac1: str, frac2: str}",
            "subtract": "Subtract frac2 from frac1. Args: {frac1: str, frac2: str}",
            "multiply": "Multiply two fractions. Args: {frac1: str, frac2: str}",
            "divide": "Divide frac1 by frac2. Args: {frac1: str, frac2: str}",
            "gcd": "Find GCD of two integers. Args: {a: int, b: int}",
            "lcm": "Find LCM of two integers. Args: {a: int, b: int}",
        }
