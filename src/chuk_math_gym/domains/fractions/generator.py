"""
Fractions domain generator.

Generates problems involving:
- Fraction simplification (reduce to lowest terms)
- Fraction addition/subtraction (common denominators)
- Fraction multiplication/division
- Mixed numbers and improper fractions
- Fraction comparison
"""

import random
import math
from typing import Optional, Tuple, List
from dataclasses import dataclass
from fractions import Fraction

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
    LiteralArgs,
    FractionArgs,
)


@dataclass
class FractionValue:
    """Represents a fraction with numerator and denominator."""

    numerator: int
    denominator: int

    def __post_init__(self):
        if self.denominator == 0:
            raise ValueError("Denominator cannot be zero")

    @property
    def value(self) -> float:
        return self.numerator / self.denominator

    def reduce(self) -> "FractionValue":
        """Return the fraction in lowest terms."""
        gcd = math.gcd(abs(self.numerator), abs(self.denominator))
        num = self.numerator // gcd
        den = self.denominator // gcd
        # Normalize sign to numerator
        if den < 0:
            num, den = -num, -den
        return FractionValue(num, den)

    def to_string(self) -> str:
        """Convert to string representation."""
        if self.denominator == 1:
            return str(self.numerator)
        return f"{self.numerator}/{self.denominator}"

    def to_mixed_string(self) -> str:
        """Convert to mixed number if applicable."""
        if abs(self.numerator) < abs(self.denominator):
            return self.to_string()
        whole = self.numerator // self.denominator
        remainder = abs(self.numerator) % abs(self.denominator)
        if remainder == 0:
            return str(whole)
        return f"{whole} {remainder}/{abs(self.denominator)}"

    @classmethod
    def from_python_fraction(cls, f: Fraction) -> "FractionValue":
        return cls(f.numerator, f.denominator)

    def to_python_fraction(self) -> Fraction:
        return Fraction(self.numerator, self.denominator)


# Problem type enumeration
class FractionProblemType:
    SIMPLIFY = "simplify"
    ADD = "add"
    SUBTRACT = "subtract"
    MULTIPLY = "multiply"
    DIVIDE = "divide"
    COMPARE = "compare"
    MIXED_TO_IMPROPER = "mixed_to_improper"
    IMPROPER_TO_MIXED = "improper_to_mixed"


# Difficulty configuration
FRACTION_DIFFICULTY_CONFIG = {
    DifficultyLevel.VERY_EASY: {
        "max_denominator": 10,
        "max_numerator": 10,
        "operations": [FractionProblemType.SIMPLIFY],
        "same_denominator": True,
    },
    DifficultyLevel.EASY: {
        "max_denominator": 12,
        "max_numerator": 20,
        "operations": [
            FractionProblemType.SIMPLIFY,
            FractionProblemType.ADD,
            FractionProblemType.SUBTRACT,
        ],
        "same_denominator": True,
    },
    DifficultyLevel.PRETTY_EASY: {
        "max_denominator": 12,
        "max_numerator": 24,
        "operations": [
            FractionProblemType.ADD,
            FractionProblemType.SUBTRACT,
            FractionProblemType.MULTIPLY,
        ],
        "same_denominator": False,
    },
    DifficultyLevel.MEDIUM: {
        "max_denominator": 20,
        "max_numerator": 50,
        "operations": [
            FractionProblemType.ADD,
            FractionProblemType.SUBTRACT,
            FractionProblemType.MULTIPLY,
            FractionProblemType.DIVIDE,
        ],
        "same_denominator": False,
    },
    DifficultyLevel.HARD: {
        "max_denominator": 50,
        "max_numerator": 100,
        "operations": [
            FractionProblemType.ADD,
            FractionProblemType.SUBTRACT,
            FractionProblemType.MULTIPLY,
            FractionProblemType.DIVIDE,
        ],
        "same_denominator": False,
        "include_negatives": True,
    },
    DifficultyLevel.PRETTY_HARD: {
        "max_denominator": 100,
        "max_numerator": 200,
        "operations": [
            FractionProblemType.ADD,
            FractionProblemType.SUBTRACT,
            FractionProblemType.MULTIPLY,
            FractionProblemType.DIVIDE,
        ],
        "same_denominator": False,
        "include_negatives": True,
        "multi_step": True,
    },
    DifficultyLevel.VERY_HARD: {
        "max_denominator": 100,
        "max_numerator": 500,
        "operations": [
            FractionProblemType.ADD,
            FractionProblemType.SUBTRACT,
            FractionProblemType.MULTIPLY,
            FractionProblemType.DIVIDE,
        ],
        "same_denominator": False,
        "include_negatives": True,
        "multi_step": True,
    },
}


# Question templates
FRACTION_TEMPLATES = {
    FractionProblemType.SIMPLIFY: [
        "Simplify the fraction {frac1}",
        "Reduce {frac1} to lowest terms",
        "What is {frac1} in simplest form?",
    ],
    FractionProblemType.ADD: [
        "What is {frac1} + {frac2}?",
        "Add {frac1} and {frac2}",
        "Calculate {frac1} + {frac2}",
    ],
    FractionProblemType.SUBTRACT: [
        "What is {frac1} - {frac2}?",
        "Subtract {frac2} from {frac1}",
        "Calculate {frac1} - {frac2}",
    ],
    FractionProblemType.MULTIPLY: [
        "What is {frac1} × {frac2}?",
        "Multiply {frac1} by {frac2}",
        "Calculate {frac1} × {frac2}",
    ],
    FractionProblemType.DIVIDE: [
        "What is {frac1} ÷ {frac2}?",
        "Divide {frac1} by {frac2}",
        "Calculate {frac1} ÷ {frac2}",
    ],
}


class FractionsGenerator:
    """
    Generator for fraction problems.

    Produces Problem and Trace objects for various fraction operations.
    """

    def __init__(self):
        self._rng = random.Random()

    def generate(
        self,
        seed: Optional[int] = None,
        difficulty: DifficultyLevel = DifficultyLevel.MEDIUM,
        problem_type: Optional[str] = None,
        tool_policy: ToolPolicy = ToolPolicy.ALLOWED,
    ) -> Tuple[Problem, Trace]:
        """
        Generate a fraction problem and its solution trace.

        Args:
            seed: Random seed for reproducibility
            difficulty: Difficulty level
            problem_type: Specific problem type (or None for random)
            tool_policy: Tool usage policy

        Returns:
            Tuple of (Problem, Trace)
        """
        if seed is None:
            seed = random.randint(0, 2**31 - 1)
        self._rng.seed(seed)

        config = FRACTION_DIFFICULTY_CONFIG[difficulty]

        # Select problem type
        if problem_type is None:
            problem_type = self._rng.choice(config["operations"])

        # Generate the problem based on type
        if problem_type == FractionProblemType.SIMPLIFY:
            return self._generate_simplify(seed, difficulty, config, tool_policy)
        elif problem_type == FractionProblemType.ADD:
            return self._generate_binary_op(seed, difficulty, config, "+", tool_policy)
        elif problem_type == FractionProblemType.SUBTRACT:
            return self._generate_binary_op(seed, difficulty, config, "-", tool_policy)
        elif problem_type == FractionProblemType.MULTIPLY:
            return self._generate_binary_op(seed, difficulty, config, "*", tool_policy)
        elif problem_type == FractionProblemType.DIVIDE:
            return self._generate_binary_op(seed, difficulty, config, "/", tool_policy)
        else:
            # Default to simplify
            return self._generate_simplify(seed, difficulty, config, tool_policy)

    def _generate_fraction(self, config: dict, reducible: bool = False) -> FractionValue:
        """Generate a random fraction based on config."""
        max_num = config["max_numerator"]
        max_den = config["max_denominator"]
        include_neg = config.get("include_negatives", False)

        denominator = self._rng.randint(2, max_den)

        if reducible:
            # Ensure fraction is reducible by multiplying by a factor
            factor = self._rng.randint(2, min(5, max_num // denominator + 1))
            base_num = self._rng.randint(1, max(1, max_num // factor))
            base_den = self._rng.randint(2, max(2, max_den // factor))
            numerator = base_num * factor
            denominator = base_den * factor
        else:
            numerator = self._rng.randint(1, max_num)

        if include_neg and self._rng.random() < 0.3:
            numerator = -numerator

        return FractionValue(numerator, denominator)

    def _generate_simplify(
        self,
        seed: int,
        difficulty: DifficultyLevel,
        config: dict,
        tool_policy: ToolPolicy,
    ) -> Tuple[Problem, Trace]:
        """Generate a fraction simplification problem."""
        # Generate a reducible fraction
        frac = self._generate_fraction(config, reducible=True)
        reduced = frac.reduce()

        # Create prompt
        template = self._rng.choice(FRACTION_TEMPLATES[FractionProblemType.SIMPLIFY])
        prompt = template.format(frac1=frac.to_string())

        # Create expression
        expression = frac.to_string()

        problem = Problem(
            id=f"fractions_{difficulty.value}_{seed}",
            seed=seed,
            domain=DomainType.FRACTIONS,
            difficulty=difficulty,
            prompt=prompt,
            expression=expression,
            answer_type=AnswerType.EXPRESSION,
            gold_answer=reduced.to_string(),
            tool_policy=tool_policy,
            tags=["fractions", "simplify", difficulty.value],
            common_mistakes=["unreduced_fraction", "wrong_gcd"],
        )

        # Generate trace
        trace = self._generate_simplify_trace(frac, reduced, problem.id)

        return problem, trace

    def _generate_binary_op(
        self,
        seed: int,
        difficulty: DifficultyLevel,
        config: dict,
        operator: str,
        tool_policy: ToolPolicy,
    ) -> Tuple[Problem, Trace]:
        """Generate a binary operation problem (+, -, *, /)."""
        frac1 = self._generate_fraction(config)
        frac2 = self._generate_fraction(config)

        # Ensure we don't divide by zero
        if operator == "/" and frac2.numerator == 0:
            frac2 = FractionValue(1, frac2.denominator)

        # For easier addition/subtraction, sometimes use same denominator
        if config.get("same_denominator", False) and operator in ["+", "-"]:
            frac2 = FractionValue(self._rng.randint(1, config["max_numerator"]), frac1.denominator)

        # Compute result using Python's Fraction for accuracy
        pf1 = frac1.to_python_fraction()
        pf2 = frac2.to_python_fraction()

        if operator == "+":
            result_pf = pf1 + pf2
            op_name = "add"
            op_symbol = "+"
            templates = FRACTION_TEMPLATES[FractionProblemType.ADD]
        elif operator == "-":
            result_pf = pf1 - pf2
            op_name = "subtract"
            op_symbol = "-"
            templates = FRACTION_TEMPLATES[FractionProblemType.SUBTRACT]
        elif operator == "*":
            result_pf = pf1 * pf2
            op_name = "multiply"
            op_symbol = "×"
            templates = FRACTION_TEMPLATES[FractionProblemType.MULTIPLY]
        else:  # "/"
            result_pf = pf1 / pf2
            op_name = "divide"
            op_symbol = "÷"
            templates = FRACTION_TEMPLATES[FractionProblemType.DIVIDE]

        result = FractionValue.from_python_fraction(result_pf)

        # Create prompt
        template = self._rng.choice(templates)
        prompt = template.format(frac1=frac1.to_string(), frac2=frac2.to_string())

        expression = f"{frac1.to_string()} {op_symbol} {frac2.to_string()}"

        problem = Problem(
            id=f"fractions_{difficulty.value}_{seed}",
            seed=seed,
            domain=DomainType.FRACTIONS,
            difficulty=difficulty,
            prompt=prompt,
            expression=expression,
            answer_type=AnswerType.EXPRESSION,
            gold_answer=result.to_string(),
            tool_policy=tool_policy,
            tags=["fractions", op_name, difficulty.value],
            common_mistakes=self._get_op_mistakes(operator),
        )

        # Generate trace
        trace = self._generate_binary_op_trace(frac1, frac2, operator, result, problem.id)

        return problem, trace

    def _generate_simplify_trace(
        self,
        original: FractionValue,
        reduced: FractionValue,
        problem_id: str,
    ) -> Trace:
        """Generate trace for simplification."""
        steps = []

        # Step 0: Identify the numerator
        steps.append(
            Step(
                index=0,
                operation=StepOperation.LITERAL,
                before_state=f"numerator = {original.numerator}",
                after_state=str(original.numerator),
                args=LiteralArgs(value=float(original.numerator), source="numerator"),
                input_refs=[],
                output_value=float(original.numerator),
                difficulty_cost=0.25,
            )
        )

        # Step 1: Identify the denominator
        steps.append(
            Step(
                index=1,
                operation=StepOperation.LITERAL,
                before_state=f"denominator = {original.denominator}",
                after_state=str(original.denominator),
                args=LiteralArgs(value=float(original.denominator), source="denominator"),
                input_refs=[],
                output_value=float(original.denominator),
                difficulty_cost=0.25,
            )
        )

        # Step 2: Find GCD
        gcd = math.gcd(abs(original.numerator), abs(original.denominator))
        steps.append(
            Step(
                index=2,
                operation=StepOperation.EVAL,
                before_state=f"GCD({abs(original.numerator)}, {abs(original.denominator)})",
                after_state=str(gcd),
                rule_id=RuleID.FIND_GCD,
                args=FractionArgs(
                    numerator=abs(original.numerator),
                    denominator=abs(original.denominator),
                    gcd=gcd,
                ),
                input_refs=[StepRef(step_index=0), StepRef(step_index=1)],
                output_value=float(gcd),
                difficulty_cost=1.0,
            )
        )

        # Step 3: Divide numerator by GCD
        new_num = original.numerator // gcd
        steps.append(
            Step(
                index=3,
                operation=StepOperation.DIVIDE,
                before_state=f"{original.numerator} ÷ {gcd}",
                after_state=str(new_num),
                rule_id=RuleID.REDUCE_NUMERATOR,
                args=FractionArgs(numerator=original.numerator, gcd=gcd),
                input_refs=[StepRef(step_index=0), StepRef(step_index=2)],
                output_value=float(new_num),
                difficulty_cost=0.5,
            )
        )

        # Step 4: Divide denominator by GCD
        new_den = original.denominator // gcd
        steps.append(
            Step(
                index=4,
                operation=StepOperation.DIVIDE,
                before_state=f"{original.denominator} ÷ {gcd}",
                after_state=str(new_den),
                rule_id=RuleID.REDUCE_DENOMINATOR,
                args=FractionArgs(denominator=original.denominator, gcd=gcd),
                input_refs=[StepRef(step_index=1), StepRef(step_index=2)],
                output_value=float(new_den),
                difficulty_cost=0.5,
            )
        )

        # Step 5: Form reduced fraction
        steps.append(
            Step(
                index=5,
                operation=StepOperation.SIMPLIFY,
                before_state=f"{new_num}/{new_den}",
                after_state=reduced.to_string(),
                rule_id=RuleID.FORM_FRACTION,
                args=FractionArgs(numerator=new_num, denominator=new_den),
                input_refs=[StepRef(step_index=3), StepRef(step_index=4)],
                output_value=reduced.value,
                difficulty_cost=0.25,
            )
        )

        return Trace(
            problem_id=problem_id,
            steps=steps,
            checkpoints=[2, 5],  # GCD finding and final result
        )

    def _generate_binary_op_trace(
        self,
        frac1: FractionValue,
        frac2: FractionValue,
        operator: str,
        result: FractionValue,
        problem_id: str,
    ) -> Trace:
        """Generate trace for binary operations."""
        steps = []
        step_idx = 0

        # Step 0: Record first fraction
        steps.append(
            Step(
                index=step_idx,
                operation=StepOperation.LITERAL,
                before_state=frac1.to_string(),
                after_state=str(frac1.value),
                args=LiteralArgs(value=frac1.value, source="fraction1"),
                input_refs=[],
                output_value=frac1.value,
                difficulty_cost=0.25,
            )
        )
        step_idx += 1

        # Step 1: Record second fraction
        steps.append(
            Step(
                index=step_idx,
                operation=StepOperation.LITERAL,
                before_state=frac2.to_string(),
                after_state=str(frac2.value),
                args=LiteralArgs(value=frac2.value, source="fraction2"),
                input_refs=[],
                output_value=frac2.value,
                difficulty_cost=0.25,
            )
        )
        step_idx += 1

        if operator in ["+", "-"]:
            # Find common denominator
            lcm = (frac1.denominator * frac2.denominator) // math.gcd(
                frac1.denominator, frac2.denominator
            )

            steps.append(
                Step(
                    index=step_idx,
                    operation=StepOperation.COMMON_DENOM,
                    before_state=f"LCD({frac1.denominator}, {frac2.denominator})",
                    after_state=str(lcm),
                    rule_id=RuleID.FIND_LCM,
                    args=FractionArgs(denominator=frac1.denominator, lcm=lcm),
                    input_refs=[StepRef(step_index=0), StepRef(step_index=1)],
                    output_value=float(lcm),
                    difficulty_cost=1.0,
                )
            )
            step_idx += 1

            # Convert fractions
            new_num1 = frac1.numerator * (lcm // frac1.denominator)
            new_num2 = frac2.numerator * (lcm // frac2.denominator)

            steps.append(
                Step(
                    index=step_idx,
                    operation=StepOperation.REWRITE,
                    before_state=f"{frac1.to_string()} = {new_num1}/{lcm}",
                    after_state=f"{new_num1}/{lcm}",
                    rule_id=RuleID.CONVERT_FRACTION,
                    args=FractionArgs(numerator=new_num1, denominator=lcm),
                    input_refs=[StepRef(step_index=0), StepRef(step_index=2)],
                    output_value=float(new_num1),
                    difficulty_cost=0.5,
                )
            )
            step_idx += 1

            steps.append(
                Step(
                    index=step_idx,
                    operation=StepOperation.REWRITE,
                    before_state=f"{frac2.to_string()} = {new_num2}/{lcm}",
                    after_state=f"{new_num2}/{lcm}",
                    rule_id=RuleID.CONVERT_FRACTION,
                    args=FractionArgs(numerator=new_num2, denominator=lcm),
                    input_refs=[StepRef(step_index=1), StepRef(step_index=2)],
                    output_value=float(new_num2),
                    difficulty_cost=0.5,
                )
            )
            step_idx += 1

            # Perform operation
            if operator == "+":
                result_num = new_num1 + new_num2
                op_step = StepOperation.ADD
                rule = RuleID.ADD_FRACTIONS
            else:
                result_num = new_num1 - new_num2
                op_step = StepOperation.SUBTRACT
                rule = RuleID.SUBTRACT_FRACTIONS

            steps.append(
                Step(
                    index=step_idx,
                    operation=op_step,
                    before_state=f"{new_num1}/{lcm} {operator} {new_num2}/{lcm}",
                    after_state=f"{result_num}/{lcm}",
                    rule_id=rule,
                    args=FractionArgs(numerator=result_num, denominator=lcm),
                    input_refs=[StepRef(step_index=step_idx - 2), StepRef(step_index=step_idx - 1)],
                    output_value=float(result_num),
                    difficulty_cost=0.75,
                )
            )
            step_idx += 1

        elif operator == "*":
            # Multiply numerators
            result_num = frac1.numerator * frac2.numerator
            steps.append(
                Step(
                    index=step_idx,
                    operation=StepOperation.MULTIPLY,
                    before_state=f"{frac1.numerator} × {frac2.numerator}",
                    after_state=str(result_num),
                    rule_id=RuleID.MULTIPLY_FRACTIONS,
                    args=FractionArgs(numerator=result_num),
                    input_refs=[StepRef(step_index=0), StepRef(step_index=1)],
                    output_value=float(result_num),
                    difficulty_cost=0.5,
                )
            )
            step_idx += 1

            # Multiply denominators
            result_den = frac1.denominator * frac2.denominator
            steps.append(
                Step(
                    index=step_idx,
                    operation=StepOperation.MULTIPLY,
                    before_state=f"{frac1.denominator} × {frac2.denominator}",
                    after_state=str(result_den),
                    rule_id=RuleID.MULTIPLY_FRACTIONS,
                    args=FractionArgs(denominator=result_den),
                    input_refs=[StepRef(step_index=0), StepRef(step_index=1)],
                    output_value=float(result_den),
                    difficulty_cost=0.5,
                )
            )
            step_idx += 1

        else:  # Division
            # Invert second fraction
            steps.append(
                Step(
                    index=step_idx,
                    operation=StepOperation.INVERT,
                    before_state=frac2.to_string(),
                    after_state=f"{frac2.denominator}/{frac2.numerator}",
                    rule_id=RuleID.DIVIDE_FRACTIONS,
                    args=FractionArgs(numerator=frac2.denominator, denominator=frac2.numerator),
                    input_refs=[StepRef(step_index=1)],
                    output_value=frac2.denominator / frac2.numerator,
                    difficulty_cost=0.5,
                )
            )
            step_idx += 1

            # Multiply
            result_num = frac1.numerator * frac2.denominator
            result_den = frac1.denominator * frac2.numerator
            steps.append(
                Step(
                    index=step_idx,
                    operation=StepOperation.MULTIPLY,
                    before_state=f"{frac1.to_string()} × {frac2.denominator}/{frac2.numerator}",
                    after_state=f"{result_num}/{result_den}",
                    rule_id=RuleID.MULTIPLY_FRACTIONS,
                    args=FractionArgs(numerator=result_num, denominator=result_den),
                    input_refs=[StepRef(step_index=0), StepRef(step_index=step_idx - 1)],
                    output_value=float(result_num),
                    difficulty_cost=0.75,
                )
            )
            step_idx += 1

        # Final simplification
        steps.append(
            Step(
                index=step_idx,
                operation=StepOperation.REDUCE,
                before_state="simplify result",
                after_state=result.to_string(),
                rule_id=RuleID.SIMPLIFY_RESULT,
                args=FractionArgs(numerator=result.numerator, denominator=result.denominator),
                input_refs=[StepRef(step_index=step_idx - 1)],
                output_value=result.value,
                difficulty_cost=0.5,
            )
        )

        return Trace(
            problem_id=problem_id,
            steps=steps,
            checkpoints=[len(steps) - 1],
        )

    def _get_op_mistakes(self, operator: str) -> List[str]:
        """Get common mistakes for an operation."""
        if operator in ["+", "-"]:
            return ["wrong_denominator", "forgot_common_denominator", "numerator_error"]
        elif operator == "*":
            return ["added_instead_of_multiplied", "unreduced_fraction"]
        else:  # /
            return ["forgot_to_invert", "division_error", "unreduced_fraction"]

    def generate_batch(
        self,
        count: int,
        difficulty: DifficultyLevel = DifficultyLevel.MEDIUM,
        start_seed: Optional[int] = None,
    ) -> List[Tuple[Problem, Trace]]:
        """Generate a batch of problems."""
        if start_seed is None:
            start_seed = random.randint(0, 2**31 - 1)

        return [self.generate(seed=start_seed + i, difficulty=difficulty) for i in range(count)]
