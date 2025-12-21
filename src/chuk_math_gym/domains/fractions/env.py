"""
Fractions Gym environment.

Implements the MathGymEnv interface for fraction problems.
"""

from chuk_math_gym.schemas.problem import Problem, DifficultyLevel, ToolPolicy
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
        problem = env.reset(seed=42, difficulty=DifficultyLevel.MEDIUM)

        obs, reward, done, info = env.step("ANSWER 1/2")
    """

    def __init__(
        self,
        tool_policy: ToolPolicy = ToolPolicy.ALLOWED,
        max_steps: int = 10,
        step_penalty: float = -0.01,
        wrong_answer_penalty: float = -1.0,
        correct_reward: float = 1.0,
        efficiency_bonus: float = 0.1,
        require_reduced: bool = True,
    ):
        """
        Initialize the fractions environment.

        Args:
            tool_policy: Default tool policy
            max_steps: Maximum steps per episode
            step_penalty: Small penalty per step
            wrong_answer_penalty: Penalty for wrong answer
            correct_reward: Reward for correct answer
            efficiency_bonus: Bonus for efficient solutions
            require_reduced: Whether answers must be in reduced form
        """
        super().__init__(
            tool_policy=tool_policy,
            max_steps=max_steps,
            step_penalty=step_penalty,
            wrong_answer_penalty=wrong_answer_penalty,
            correct_reward=correct_reward,
            efficiency_bonus=efficiency_bonus,
        )

        self._generator = FractionsGenerator()
        self._verifier = FractionsVerifier(require_reduced=require_reduced)

    def _generate_problem(
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

    def _generate_trace(self, problem: Problem) -> Trace:
        """Generate the solution trace for a problem."""
        _, trace = self._generator.generate(
            seed=problem.seed,
            difficulty=problem.difficulty,
            tool_policy=problem.tool_policy,
        )
        return trace

    def _get_verifier(self) -> Verifier:
        """Get the fractions verifier."""
        return self._verifier

    def _execute_tool(self, tool_name: str, args: dict) -> str:
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
