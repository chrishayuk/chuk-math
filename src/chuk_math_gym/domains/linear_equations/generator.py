"""
Linear equations domain generator.

Generates problems involving:
- One-step equations (x + 5 = 10)
- Two-step equations (2x + 5 = 15)
- Multi-step equations (3x + 2 = x + 10)
- Equations with fractions
- Equations with distribution
"""

import random
from typing import Optional, Tuple, List
from dataclasses import dataclass
from fractions import Fraction
from enum import Enum

from chuk_math_gym.schemas.problem import (
    Problem,
    DomainType,
    DifficultyLevel,
    AnswerType,
    ToolPolicy,
)
from chuk_math_gym.schemas.trace import (
    Step,
    Trace,
    StepOperation,
    StepRef,
    RuleID,
    EquationTransformArgs,
)


class EquationType(str, Enum):
    """Types of linear equations."""
    ONE_STEP_ADD = "one_step_add"       # x + a = b
    ONE_STEP_SUB = "one_step_sub"       # x - a = b
    ONE_STEP_MUL = "one_step_mul"       # ax = b
    ONE_STEP_DIV = "one_step_div"       # x/a = b
    TWO_STEP = "two_step"               # ax + b = c
    VARIABLE_BOTH_SIDES = "var_both"    # ax + b = cx + d
    DISTRIBUTION = "distribution"        # a(x + b) = c
    FRACTIONAL = "fractional"           # x/a + b = c


@dataclass
class LinearEquation:
    """Represents a linear equation ax + b = c or ax + b = cx + d."""
    # Left side: a*x + b
    a: Fraction  # coefficient of x on left
    b: Fraction  # constant on left

    # Right side: c*x + d
    c: Fraction  # coefficient of x on right (usually 0)
    d: Fraction  # constant on right

    variable: str = "x"

    @property
    def solution(self) -> Optional[Fraction]:
        """Solve for x: (a-c)x + b = d => x = (d-b)/(a-c)"""
        coeff = self.a - self.c
        const = self.d - self.b
        if coeff == 0:
            return None  # No solution or infinite solutions
        return const / coeff

    def to_string(self) -> str:
        """Convert to equation string."""
        left = self._format_side(self.a, self.b, self.variable)
        right = self._format_side(self.c, self.d, self.variable)
        return f"{left} = {right}"

    def _format_side(self, coeff: Fraction, const: Fraction, var: str) -> str:
        """Format one side of the equation."""
        parts = []

        if coeff != 0:
            if coeff == 1:
                parts.append(var)
            elif coeff == -1:
                parts.append(f"-{var}")
            elif coeff.denominator == 1:
                parts.append(f"{coeff.numerator}{var}")
            else:
                parts.append(f"({coeff.numerator}/{coeff.denominator}){var}")

        if const != 0 or not parts:
            if parts and const > 0:
                if const.denominator == 1:
                    parts.append(f"+ {const.numerator}")
                else:
                    parts.append(f"+ {const.numerator}/{const.denominator}")
            elif parts and const < 0:
                if const.denominator == 1:
                    parts.append(f"- {abs(const.numerator)}")
                else:
                    parts.append(f"- {abs(const.numerator)}/{const.denominator}")
            else:
                if const.denominator == 1:
                    parts.append(str(const.numerator))
                else:
                    parts.append(f"{const.numerator}/{const.denominator}")

        return " ".join(parts)


# Difficulty configuration
LINEAR_EQ_DIFFICULTY_CONFIG = {
    DifficultyLevel.VERY_EASY: {
        "types": [EquationType.ONE_STEP_ADD, EquationType.ONE_STEP_SUB],
        "max_coeff": 1,
        "max_const": 20,
        "integer_solutions": True,
        "positive_only": True,
    },
    DifficultyLevel.EASY: {
        "types": [EquationType.ONE_STEP_ADD, EquationType.ONE_STEP_SUB, EquationType.ONE_STEP_MUL],
        "max_coeff": 10,
        "max_const": 50,
        "integer_solutions": True,
        "positive_only": True,
    },
    DifficultyLevel.PRETTY_EASY: {
        "types": [EquationType.ONE_STEP_MUL, EquationType.ONE_STEP_DIV, EquationType.TWO_STEP],
        "max_coeff": 12,
        "max_const": 100,
        "integer_solutions": True,
        "positive_only": False,
    },
    DifficultyLevel.MEDIUM: {
        "types": [EquationType.TWO_STEP, EquationType.VARIABLE_BOTH_SIDES],
        "max_coeff": 15,
        "max_const": 100,
        "integer_solutions": True,
        "positive_only": False,
    },
    DifficultyLevel.HARD: {
        "types": [EquationType.TWO_STEP, EquationType.VARIABLE_BOTH_SIDES, EquationType.DISTRIBUTION],
        "max_coeff": 20,
        "max_const": 200,
        "integer_solutions": False,
        "positive_only": False,
    },
    DifficultyLevel.PRETTY_HARD: {
        "types": [EquationType.VARIABLE_BOTH_SIDES, EquationType.DISTRIBUTION, EquationType.FRACTIONAL],
        "max_coeff": 30,
        "max_const": 500,
        "integer_solutions": False,
        "positive_only": False,
    },
    DifficultyLevel.VERY_HARD: {
        "types": [EquationType.DISTRIBUTION, EquationType.FRACTIONAL, EquationType.VARIABLE_BOTH_SIDES],
        "max_coeff": 50,
        "max_const": 1000,
        "integer_solutions": False,
        "positive_only": False,
    },
}


# Question templates
LINEAR_EQ_TEMPLATES = [
    "Solve for {var}: {equation}",
    "Find {var} if {equation}",
    "What is {var} in the equation {equation}?",
    "Solve: {equation}",
]


class LinearEquationsGenerator:
    """
    Generator for linear equation problems.

    Produces Problem and Trace objects for various equation types.
    """

    def __init__(self):
        self._rng = random.Random()

    def generate(
        self,
        seed: Optional[int] = None,
        difficulty: DifficultyLevel = DifficultyLevel.MEDIUM,
        equation_type: Optional[EquationType] = None,
        tool_policy: ToolPolicy = ToolPolicy.ALLOWED,
        _retry_count: int = 0,
    ) -> Tuple[Problem, Trace]:
        """
        Generate a linear equation problem and its solution trace.

        Args:
            seed: Random seed for reproducibility
            difficulty: Difficulty level
            equation_type: Type of equation to generate
            tool_policy: Tool usage policy
            _retry_count: Internal counter to prevent infinite recursion

        Raises:
            RuntimeError: If maximum retries exceeded
        """
        MAX_RETRIES = 10

        if seed is None:
            seed = random.randint(0, 2**31 - 1)
        self._rng.seed(seed)

        config = LINEAR_EQ_DIFFICULTY_CONFIG[difficulty]

        # Select equation type
        if equation_type is None:
            equation_type = self._rng.choice(config["types"])

        # Generate equation based on type
        equation = self._generate_equation(equation_type, config)

        solution = equation.solution
        if solution is None:
            # Retry with limit
            if _retry_count >= MAX_RETRIES:
                raise RuntimeError(
                    f"Failed to generate valid equation after {MAX_RETRIES} attempts"
                )
            return self.generate(seed + 1, difficulty, equation_type, tool_policy, _retry_count + 1)

        # Format solution
        if solution.denominator == 1:
            answer_str = str(solution.numerator)
        else:
            answer_str = f"{solution.numerator}/{solution.denominator}"

        # Create prompt
        template = self._rng.choice(LINEAR_EQ_TEMPLATES)
        prompt = template.format(var=equation.variable, equation=equation.to_string())

        problem = Problem(
            id=f"linear_{difficulty.value}_{seed}",
            seed=seed,
            domain=DomainType.LINEAR_EQUATIONS,
            difficulty=difficulty,
            prompt=prompt,
            expression=equation.to_string(),
            answer_type=AnswerType.NUMERIC if solution.denominator == 1 else AnswerType.EXPRESSION,
            gold_answer=answer_str,
            tolerance=1e-9,
            tool_policy=tool_policy,
            tags=["linear_equations", equation_type.value, difficulty.value],
            common_mistakes=self._get_common_mistakes(equation_type),
        )

        # Generate trace
        trace = self._generate_trace(equation, problem.id)

        return problem, trace

    def _generate_equation(self, eq_type: EquationType, config: dict) -> LinearEquation:
        """Generate a specific type of equation."""
        max_coeff = config["max_coeff"]
        max_const = config["max_const"]
        integer_sol = config["integer_solutions"]
        positive = config.get("positive_only", False)

        if eq_type == EquationType.ONE_STEP_ADD:
            # x + a = b, solution: x = b - a
            if integer_sol:
                x = self._rand_int(1, max_const, positive)
                a = self._rand_int(1, max_const, positive)
                b = x + a
            else:
                a = self._rand_int(1, max_const, positive)
                b = self._rand_int(1, max_const, positive)
            return LinearEquation(
                a=Fraction(1), b=Fraction(a),
                c=Fraction(0), d=Fraction(b)
            )

        elif eq_type == EquationType.ONE_STEP_SUB:
            # x - a = b, solution: x = b + a
            if integer_sol:
                x = self._rand_int(1, max_const, positive)
                a = self._rand_int(1, min(x, max_const), True)
                b = x - a
            else:
                a = self._rand_int(1, max_const, positive)
                b = self._rand_int(-max_const, max_const, False)
            return LinearEquation(
                a=Fraction(1), b=Fraction(-a),
                c=Fraction(0), d=Fraction(b)
            )

        elif eq_type == EquationType.ONE_STEP_MUL:
            # ax = b, solution: x = b/a
            if integer_sol:
                a = self._rand_int(2, max_coeff, True)
                x = self._rand_int(1, max_const // a, positive)
                b = a * x
            else:
                a = self._rand_int(2, max_coeff, True)
                b = self._rand_int(1, max_const, positive)
            return LinearEquation(
                a=Fraction(a), b=Fraction(0),
                c=Fraction(0), d=Fraction(b)
            )

        elif eq_type == EquationType.ONE_STEP_DIV:
            # x/a = b, solution: x = ab
            a = self._rand_int(2, max_coeff, True)
            if integer_sol:
                b = self._rand_int(1, max_const // a, positive)
            else:
                b = self._rand_int(1, max_const, positive)
            return LinearEquation(
                a=Fraction(1, a), b=Fraction(0),
                c=Fraction(0), d=Fraction(b)
            )

        elif eq_type == EquationType.TWO_STEP:
            # ax + b = c, solution: x = (c-b)/a
            if integer_sol:
                a = self._rand_int(2, max_coeff, True)
                x = self._rand_int(1, max_const // a, positive)
                b = self._rand_int(-max_const, max_const, False)
                c = a * x + b
            else:
                a = self._rand_int(2, max_coeff, True)
                b = self._rand_int(-max_const, max_const, False)
                c = self._rand_int(-max_const, max_const, False)
            return LinearEquation(
                a=Fraction(a), b=Fraction(b),
                c=Fraction(0), d=Fraction(c)
            )

        elif eq_type == EquationType.VARIABLE_BOTH_SIDES:
            # ax + b = cx + d, solution: x = (d-b)/(a-c)
            if integer_sol:
                x = self._rand_int(1, max_const, positive)
                a = self._rand_int(2, max_coeff, True)
                c = self._rand_int(1, a - 1, True)  # Ensure a > c
                b = self._rand_int(-max_const, max_const, False)
                d = (a - c) * x + b
            else:
                a = self._rand_int(2, max_coeff, True)
                c = self._rand_int(1, max_coeff, True)
                if a == c:
                    c = a + 1  # Ensure different coefficients
                b = self._rand_int(-max_const, max_const, False)
                d = self._rand_int(-max_const, max_const, False)
            return LinearEquation(
                a=Fraction(a), b=Fraction(b),
                c=Fraction(c), d=Fraction(d)
            )

        elif eq_type == EquationType.DISTRIBUTION:
            # a(x + b) = c => ax + ab = c
            if integer_sol:
                x = self._rand_int(1, max_const, positive)
                a = self._rand_int(2, max_coeff, True)
                b = self._rand_int(-max_const // a, max_const // a, False)
                c = a * (x + b)
            else:
                a = self._rand_int(2, max_coeff, True)
                b = self._rand_int(-max_const, max_const, False)
                c = self._rand_int(-max_const, max_const, False)
            return LinearEquation(
                a=Fraction(a), b=Fraction(a * b),
                c=Fraction(0), d=Fraction(c)
            )

        else:  # FRACTIONAL
            # x/a + b = c
            a = self._rand_int(2, max_coeff, True)
            if integer_sol:
                x = self._rand_int(1, max_const, positive) * a  # Ensure x divisible by a
                b = self._rand_int(-max_const, max_const, False)
                c = x // a + b
            else:
                b = self._rand_int(-max_const, max_const, False)
                c = self._rand_int(-max_const, max_const, False)
            return LinearEquation(
                a=Fraction(1, a), b=Fraction(b),
                c=Fraction(0), d=Fraction(c)
            )

    def _rand_int(self, low: int, high: int, positive: bool) -> int:
        """Generate random integer."""
        if positive:
            return self._rng.randint(max(1, low), max(1, high))
        return self._rng.randint(low, high)

    def _generate_trace(self, equation: LinearEquation, problem_id: str) -> Trace:
        """Generate solution trace for a linear equation."""
        steps = []
        step_idx = 0

        # Record initial equation state
        # Left side: ax + b
        # Right side: cx + d

        # Step 1: Move variables to left side (if needed)
        if equation.c != 0:
            # Subtract cx from both sides
            new_a = equation.a - equation.c
            steps.append(Step(
                index=step_idx,
                operation=StepOperation.SUB_BOTH,
                before_state=f"Subtract {equation.c}x from both sides",
                after_state=f"{new_a}x + {equation.b} = {equation.d}",
                rule_id=RuleID.COLLECT_VARIABLES,
                args=EquationTransformArgs(value=f"{equation.c}x", variable="x"),
                input_refs=[],
                output_value=float(new_a),
                difficulty_cost=1.0,
            ))
            step_idx += 1
            current_a = new_a
        else:
            current_a = equation.a

        # Step 2: Move constants to right side (if needed)
        if equation.b != 0:
            new_d = equation.d - equation.b

            if equation.b > 0:
                op = StepOperation.SUB_BOTH
                desc = f"Subtract {equation.b} from both sides"
            else:
                op = StepOperation.ADD_BOTH
                desc = f"Add {abs(equation.b)} to both sides"

            input_refs = [StepRef(step_index=step_idx-1)] if step_idx > 0 else []
            steps.append(Step(
                index=step_idx,
                operation=op,
                before_state=desc,
                after_state=f"{current_a}x = {new_d}",
                rule_id=RuleID.MOVE_CONSTANT,
                args=EquationTransformArgs(value=abs(equation.b), variable="x"),
                input_refs=input_refs,
                output_value=float(new_d),
                difficulty_cost=0.75,
            ))
            step_idx += 1
            current_d = new_d
        else:
            current_d = equation.d

        # Step 3: Divide by coefficient (if needed)
        solution = equation.solution

        if current_a != 1:
            input_refs = [StepRef(step_index=step_idx-1)] if step_idx > 0 else []
            steps.append(Step(
                index=step_idx,
                operation=StepOperation.DIV_BOTH,
                before_state=f"Divide both sides by {current_a}",
                after_state=f"x = {solution}",
                rule_id=RuleID.ISOLATE_VARIABLE,
                args=EquationTransformArgs(value=float(current_a), variable="x"),
                input_refs=input_refs,
                output_value=float(solution),
                difficulty_cost=0.75,
            ))
        else:
            input_refs = [StepRef(step_index=step_idx-1)] if step_idx > 0 else []
            steps.append(Step(
                index=step_idx,
                operation=StepOperation.ISOLATE,
                before_state=f"x = {current_d}",
                after_state=f"x = {solution}",
                rule_id=RuleID.ISOLATE_VARIABLE,
                args=EquationTransformArgs(value=float(current_d), variable="x"),
                input_refs=input_refs,
                output_value=float(solution),
                difficulty_cost=0.25,
            ))

        return Trace(
            problem_id=problem_id,
            steps=steps,
            checkpoints=[len(steps) - 1],
        )

    def _get_common_mistakes(self, eq_type: EquationType) -> List[str]:
        """Get common mistakes for equation type."""
        mistakes = {
            EquationType.ONE_STEP_ADD: ["sign_error", "arithmetic_error"],
            EquationType.ONE_STEP_SUB: ["sign_error", "subtracted_wrong_direction"],
            EquationType.ONE_STEP_MUL: ["division_error", "forgot_to_divide"],
            EquationType.ONE_STEP_DIV: ["multiplication_error", "inverted_operation"],
            EquationType.TWO_STEP: ["order_of_operations", "sign_error", "arithmetic_error"],
            EquationType.VARIABLE_BOTH_SIDES: ["collecting_terms_error", "sign_error"],
            EquationType.DISTRIBUTION: ["distribution_error", "forgot_to_distribute"],
            EquationType.FRACTIONAL: ["fraction_error", "wrong_common_denominator"],
        }
        return mistakes.get(eq_type, ["arithmetic_error"])

    def generate_batch(
        self,
        count: int,
        difficulty: DifficultyLevel = DifficultyLevel.MEDIUM,
        start_seed: Optional[int] = None,
    ) -> List[Tuple[Problem, Trace]]:
        """Generate a batch of problems."""
        if start_seed is None:
            start_seed = random.randint(0, 2**31 - 1)

        return [
            self.generate(seed=start_seed + i, difficulty=difficulty)
            for i in range(count)
        ]
