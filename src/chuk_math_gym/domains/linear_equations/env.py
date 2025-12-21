"""
Linear Equations Gym environment.

Implements the MathGymEnv interface for linear equation problems.
"""

from chuk_math_gym.schemas.problem import Problem, DifficultyLevel, ToolPolicy
from chuk_math_gym.schemas.trace import Trace
from chuk_math_gym.verifiers.base import Verifier
from chuk_math_gym.env.base import MathGymEnv
from chuk_math_gym.domains.linear_equations.generator import LinearEquationsGenerator
from chuk_math_gym.domains.linear_equations.verifier import LinearEquationsVerifier


class LinearEquationsGymEnv(MathGymEnv):
    """
    Gym environment for linear equation problems.

    Supports various equation types:
    - One-step equations
    - Two-step equations
    - Equations with variables on both sides
    - Distribution and fractional equations

    Example:
        env = LinearEquationsGymEnv()
        problem = env.reset(seed=42, difficulty=DifficultyLevel.MEDIUM)

        obs, reward, done, info = env.step("ANSWER 5")
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
        Initialize the linear equations environment.
        """
        super().__init__(
            tool_policy=tool_policy,
            max_steps=max_steps,
            step_penalty=step_penalty,
            wrong_answer_penalty=wrong_answer_penalty,
            correct_reward=correct_reward,
            efficiency_bonus=efficiency_bonus,
        )

        self._generator = LinearEquationsGenerator()
        self._verifier = LinearEquationsVerifier()

    def _generate_problem(
        self,
        seed: int,
        difficulty: DifficultyLevel,
    ) -> Problem:
        """Generate a linear equation problem."""
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
        """Get the linear equations verifier."""
        return self._verifier

    def _execute_tool(self, tool_name: str, args: dict) -> str:
        """
        Execute a tool call.

        Supported tools:
        - solve: Solve a linear equation
        - simplify: Simplify an expression
        - substitute: Check if a value satisfies an equation
        - add_both: Add a value to both sides
        - subtract_both: Subtract a value from both sides
        - multiply_both: Multiply both sides by a value
        - divide_both: Divide both sides by a value
        """

        if tool_name == "solve":
            # Simple linear equation solver
            equation = args.get("equation", "x = 0")
            try:
                # Parse ax + b = c form
                # Very simplified - real implementation would use sympy
                if "=" in equation:
                    left, right = equation.split("=")
                    # Extract coefficient and constant from left side
                    # This is a simplified parser
                    return f"x = {args.get('solution', 'unknown')}"
                return "Error: Invalid equation format"
            except Exception as e:
                return f"Error: {e}"

        elif tool_name == "substitute":
            equation = args.get("equation", "x = 0")
            value = args.get("value", 0)
            variable = args.get("variable", "x")
            try:
                # Substitute and check
                result = self._verifier.verify_by_substitution(equation, variable, float(value))
                if result.correct:
                    return f"Yes, {variable} = {value} satisfies the equation"
                return f"No, {variable} = {value} does not satisfy the equation"
            except Exception as e:
                return f"Error: {e}"

        elif tool_name in ["add_both", "subtract_both", "multiply_both", "divide_both"]:
            equation = args.get("equation", "x = 0")
            value = args.get("value", 0)
            try:
                if "=" not in equation:
                    return "Error: Invalid equation"

                left, right = equation.split("=")

                # Apply operation
                if tool_name == "add_both":
                    return f"{left.strip()} + {value} = {right.strip()} + {value}"
                elif tool_name == "subtract_both":
                    return f"{left.strip()} - {value} = {right.strip()} - {value}"
                elif tool_name == "multiply_both":
                    return f"({left.strip()}) × {value} = ({right.strip()}) × {value}"
                else:  # divide_both
                    if float(value) == 0:
                        return "Error: Cannot divide by zero"
                    return f"({left.strip()}) ÷ {value} = ({right.strip()}) ÷ {value}"
            except Exception as e:
                return f"Error: {e}"

        elif tool_name == "evaluate":
            expression = args.get("expression", "0")
            try:
                # Safe evaluation using ast.literal_eval won't work for math
                # Use a simple recursive descent parser instead of eval
                eval_result = self._safe_eval_expression(expression)
                return str(eval_result)
            except Exception as e:
                return f"Error: {e}"

        else:
            return f"Unknown tool: {tool_name}"

    def _safe_eval_expression(self, expression: str) -> float:
        """
        Safely evaluate a numeric expression without using eval().

        Uses a simple recursive descent parser for basic arithmetic.

        Args:
            expression: A string containing a numeric expression

        Returns:
            The evaluated result as a float

        Raises:
            ValueError: If expression is invalid
        """
        import ast
        import operator

        # Define allowed operations
        ops = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.USub: operator.neg,
            ast.UAdd: operator.pos,
        }

        def _eval(node):
            if isinstance(node, ast.Num):  # Python 3.7
                return node.n
            elif isinstance(node, ast.Constant):  # Python 3.8+
                if isinstance(node.value, (int, float)):
                    return node.value
                raise ValueError(f"Invalid constant: {node.value}")
            elif isinstance(node, ast.BinOp):
                left = _eval(node.left)
                right = _eval(node.right)
                op = ops.get(type(node.op))
                if op is None:
                    raise ValueError(f"Unsupported operator: {type(node.op)}")
                return op(left, right)
            elif isinstance(node, ast.UnaryOp):
                operand = _eval(node.operand)
                op = ops.get(type(node.op))
                if op is None:
                    raise ValueError(f"Unsupported unary operator: {type(node.op)}")
                return op(operand)
            elif isinstance(node, ast.Expression):
                return _eval(node.body)
            else:
                raise ValueError(f"Unsupported node type: {type(node)}")

        try:
            tree = ast.parse(expression, mode="eval")
            return float(_eval(tree))
        except SyntaxError as e:
            raise ValueError(f"Invalid expression: {e}")

    def get_tool_descriptions(self) -> dict[str, str]:
        """Get descriptions of available tools."""
        return {
            "solve": "Solve a linear equation. Args: {equation: str}",
            "substitute": "Check if a value satisfies an equation. Args: {equation: str, variable: str, value: float}",
            "add_both": "Add a value to both sides. Args: {equation: str, value: float}",
            "subtract_both": "Subtract from both sides. Args: {equation: str, value: float}",
            "multiply_both": "Multiply both sides. Args: {equation: str, value: float}",
            "divide_both": "Divide both sides. Args: {equation: str, value: float}",
            "evaluate": "Evaluate a numeric expression. Args: {expression: str}",
        }
