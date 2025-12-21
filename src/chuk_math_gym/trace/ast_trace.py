"""
AST-based trace generator for arithmetic expressions.

Parses expressions into an AST and generates step-by-step
traces following proper order of operations.
"""

import re
from typing import Optional, Tuple, List
from decimal import Decimal, getcontext
from dataclasses import dataclass

from chuk_math_gym.schemas.problem import Problem
from chuk_math_gym.schemas.trace import (
    Step,
    Trace,
    StepOperation,
    StepRef,
    RuleID,
    LiteralArgs,
    ArithmeticArgs,
)
from chuk_math_gym.trace.generator import TraceGenerator

# Set precision for calculations
getcontext().prec = 64


@dataclass
class ASTNode:
    """Simple AST node for expression trees."""
    value: str  # Operator or number
    left: Optional['ASTNode'] = None
    right: Optional['ASTNode'] = None
    is_unary: bool = False

    def is_leaf(self) -> bool:
        """Check if this is a leaf node (number)."""
        return self.left is None and self.right is None

    def is_operator(self) -> bool:
        """Check if this is an operator node."""
        return self.value in ['+', '-', '*', '/', '^']


class ExpressionTokenizer:
    """Tokenize arithmetic expressions."""

    def __init__(self, expression: str):
        self.expression = expression
        self.pos = 0

    def tokenize(self) -> List[str]:
        """Tokenize the expression into a list of tokens."""
        tokens = []
        while self.pos < len(self.expression):
            char = self.expression[self.pos]

            if char.isspace():
                self.pos += 1
                continue

            if char in '+-*/^()':
                tokens.append(char)
                self.pos += 1
            elif char.isdigit() or char == '.':
                tokens.append(self._read_number())
            else:
                self.pos += 1  # Skip unknown characters

        return tokens

    def _read_number(self) -> str:
        """Read a number (integer or decimal)."""
        start = self.pos
        while self.pos < len(self.expression):
            char = self.expression[self.pos]
            if char.isdigit() or char == '.' or char.lower() == 'e':
                self.pos += 1
            elif char in '+-' and self.pos > start and self.expression[self.pos-1].lower() == 'e':
                # Handle scientific notation like 1e-5
                self.pos += 1
            else:
                break
        return self.expression[start:self.pos]


class ExpressionParser:
    """
    Recursive descent parser for arithmetic expressions.
    Handles order of operations (PEMDAS).
    """

    PRECEDENCE = {
        '+': 1,
        '-': 1,
        '*': 2,
        '/': 2,
        '^': 3,
    }

    def __init__(self, tokens: List[str]):
        self.tokens = tokens
        self.pos = 0

    def parse(self) -> Optional[ASTNode]:
        """Parse tokens into an AST."""
        if not self.tokens:
            return None
        return self._parse_expression(0)

    def _current_token(self) -> Optional[str]:
        """Get current token without advancing."""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def _advance(self) -> Optional[str]:
        """Advance and return the current token."""
        token = self._current_token()
        self.pos += 1
        return token

    def _parse_expression(self, min_precedence: int) -> Optional[ASTNode]:
        """Parse an expression with precedence climbing."""
        left = self._parse_primary()

        while True:
            token = self._current_token()
            if token is None or token not in self.PRECEDENCE:
                break

            precedence = self.PRECEDENCE[token]
            if precedence < min_precedence:
                break

            operator = self._advance()
            # Right-associative for power, left-associative for others
            next_min_prec = precedence + 1 if operator != '^' else precedence
            right = self._parse_expression(next_min_prec)

            left = ASTNode(value=operator, left=left, right=right)

        return left

    def _parse_primary(self) -> Optional[ASTNode]:
        """Parse a primary expression (number, unary, or parenthesized)."""
        token = self._current_token()

        if token is None:
            return None

        # Handle unary minus/plus
        if token == '-' or token == '+':
            self._advance()
            operand = self._parse_primary()
            if token == '-':
                return ASTNode(value='-', right=operand, is_unary=True)
            return operand

        # Handle parentheses
        if token == '(':
            self._advance()
            expr = self._parse_expression(0)
            if self._current_token() == ')':
                self._advance()
            return expr

        # Handle number
        if self._is_number(token):
            self._advance()
            return ASTNode(value=token)

        return None

    def _is_number(self, token: str) -> bool:
        """Check if token is a number."""
        try:
            float(token)
            return True
        except ValueError:
            return False


class ASTTraceGenerator(TraceGenerator):
    """
    Generates solution traces from AST-based expression evaluation.

    Walks the expression tree and generates a step for each operation,
    following proper order of operations.
    """

    OPERATOR_TO_STEP = {
        '+': StepOperation.ADD,
        '-': StepOperation.SUBTRACT,
        '*': StepOperation.MULTIPLY,
        '/': StepOperation.DIVIDE,
        '^': StepOperation.POWER,
    }

    def __init__(self):
        self._step_counter = 0
        self._steps: List[Step] = []

    def generate(self, problem: Problem) -> Trace:
        """Generate a trace from a Problem."""
        if problem.expression:
            return self.generate_from_expression(problem.expression, problem.id)
        else:
            # Extract expression from prompt if not available
            # This is a fallback - ideally expression should be set
            expr = self._extract_expression(problem.prompt)
            return self.generate_from_expression(expr, problem.id)

    def generate_from_expression(self, expression: str, problem_id: str) -> Trace:
        """
        Generate a trace from an expression string.

        Parses the expression into an AST and evaluates it step by step.

        Args:
            expression: The mathematical expression to trace
            problem_id: ID of the problem this trace belongs to

        Returns:
            A Trace object with all solution steps

        Raises:
            ZeroDivisionError: If expression contains division by zero
            ValueError: If expression is malformed
        """
        # Reset state
        self._step_counter = 0
        self._steps = []

        # Tokenize and parse
        try:
            tokenizer = ExpressionTokenizer(expression)
            tokens = tokenizer.tokenize()
            parser = ExpressionParser(tokens)
            ast = parser.parse()
        except (ValueError, IndexError, KeyError, TypeError, AttributeError):
            # Return empty trace on parse error
            # These exceptions cover: malformed expressions, token access errors,
            # missing keys in AST nodes, type mismatches, and None access
            return Trace(
                problem_id=problem_id,
                steps=[],
            )

        if ast is None:
            # Empty or invalid expression
            return Trace(
                problem_id=problem_id,
                steps=[],
            )

        # Evaluate AST and generate steps
        # ZeroDivisionError propagates up - caller should handle or prevent
        self._evaluate_node(ast)

        # Identify checkpoints (operations on operations are key steps)
        checkpoints = self._identify_checkpoints()

        return Trace(
            problem_id=problem_id,
            steps=self._steps,
            checkpoints=checkpoints,
            # final_step_index defaults to last step
        )

    def _evaluate_node(self, node: ASTNode) -> Tuple[int, float]:
        """
        Recursively evaluate an AST node.

        Returns (step_index, value) for this node.
        """
        if node is None:
            return -1, 0.0

        # Handle unary minus
        if node.is_unary and node.value == '-':
            right_step_idx, right_value = self._evaluate_node(node.right)
            result_value = -right_value

            step_idx = self._step_counter
            self._step_counter += 1

            step = Step(
                index=step_idx,
                operation=StepOperation.SUBTRACT,
                before_state=f"-{right_value}",
                after_state=str(result_value),
                rule_id=RuleID.UNARY_NEGATION,
                args=ArithmeticArgs(left=0.0, right=right_value, operator="-"),
                input_refs=[StepRef(step_index=right_step_idx)] if right_step_idx >= 0 else [],
                output_value=result_value,
                difficulty_cost=0.5,
            )
            self._steps.append(step)
            return step_idx, result_value

        # Handle leaf nodes (literals)
        if node.is_leaf():
            value = float(node.value)
            step_idx = self._step_counter
            self._step_counter += 1

            step = Step(
                index=step_idx,
                operation=StepOperation.LITERAL,
                before_state=node.value,
                after_state=str(value),
                args=LiteralArgs(value=value, source="expression"),
                input_refs=[],
                output_value=value,
                difficulty_cost=0.25,
            )
            self._steps.append(step)
            return step_idx, value

        # Handle binary operators
        if node.is_operator():
            # Evaluate children first (post-order traversal)
            left_step_idx, left_value = self._evaluate_node(node.left)
            right_step_idx, right_value = self._evaluate_node(node.right)

            # Perform operation
            result_value = self._compute(node.value, left_value, right_value)

            step_idx = self._step_counter
            self._step_counter += 1

            # Determine operation type
            op_type = self.OPERATOR_TO_STEP.get(node.value, StepOperation.EVAL)

            # Format before state
            left_str = self._format_number(left_value)
            right_str = self._format_number(right_value)
            before_state = f"({left_str} {node.value} {right_str})"

            # Compute difficulty based on operation and values
            difficulty = self._compute_step_difficulty(node.value, left_value, right_value)

            # Build input refs
            input_refs = []
            if left_step_idx >= 0:
                input_refs.append(StepRef(step_index=left_step_idx))
            if right_step_idx >= 0:
                input_refs.append(StepRef(step_index=right_step_idx))

            step = Step(
                index=step_idx,
                operation=op_type,
                before_state=before_state,
                after_state=str(result_value),
                args=ArithmeticArgs(left=left_value, right=right_value, operator=node.value),
                input_refs=input_refs,
                output_value=result_value,
                difficulty_cost=difficulty,
                common_mistake_here=self._get_common_mistake(node.value),
            )
            self._steps.append(step)
            return step_idx, result_value

        # Fallback
        return -1, 0.0

    def _compute(self, operator: str, left: float, right: float) -> float:
        """
        Compute the result of a binary operation.

        Args:
            operator: The operator (+, -, *, /, ^)
            left: Left operand
            right: Right operand

        Returns:
            Result of the operation

        Raises:
            ZeroDivisionError: If dividing by zero
            ValueError: If operator is unknown
        """
        if operator == '+':
            return left + right
        elif operator == '-':
            return left - right
        elif operator == '*':
            return left * right
        elif operator == '/':
            if right == 0:
                raise ZeroDivisionError(f"Division by zero: {left} / {right}")
            return left / right
        elif operator == '^':
            if left == 0 and right < 0:
                raise ZeroDivisionError(f"Zero raised to negative power: {left} ^ {right}")
            return left ** right
        else:
            raise ValueError(f"Unknown operator: {operator}")

    def _format_number(self, value: float) -> str:
        """Format a number for display."""
        if value == int(value):
            return str(int(value))
        return f"{value:.6g}"

    def _compute_step_difficulty(self, operator: str, left: float, right: float) -> float:
        """Compute difficulty cost for a step."""
        base_costs = {
            '+': 0.5,
            '-': 0.6,
            '*': 1.0,
            '/': 1.2,
            '^': 1.5,
        }
        base_cost = base_costs.get(operator, 1.0)

        # Increase cost for larger numbers
        magnitude = max(abs(left), abs(right))
        if magnitude > 1000:
            base_cost *= 1.5
        if magnitude > 10000:
            base_cost *= 1.5

        # Increase cost for decimals
        if left != int(left) or right != int(right):
            base_cost *= 1.3

        return base_cost

    def _get_common_mistake(self, operator: str) -> Optional[str]:
        """Get common mistake type for an operator."""
        mistakes = {
            '-': 'sign_error',
            '/': 'division_error',
        }
        return mistakes.get(operator)

    def _identify_checkpoints(self) -> List[int]:
        """
        Identify checkpoint steps for partial credit.

        Checkpoints are steps that involve operations on intermediate results
        (not just on literals).
        """
        checkpoints = []
        for step in self._steps:
            # Steps with multiple inputs that aren't literals are checkpoints
            if len(step.input_refs) >= 2 and step.operation != StepOperation.LITERAL:
                # Check if inputs are from other operations (not just literals)
                input_steps = [s for s in self._steps if StepRef(step_index=s.index) in step.input_refs]
                if any(s.operation != StepOperation.LITERAL for s in input_steps):
                    checkpoints.append(step.index)

        # Always include final step
        if self._steps and self._steps[-1].index not in checkpoints:
            checkpoints.append(self._steps[-1].index)

        return checkpoints

    def _extract_expression(self, prompt: str) -> str:
        """Extract expression from a prompt string."""
        # Try to find expression patterns
        patterns = [
            r'What is ([^?]+)\?',
            r'Calculate[:\s]+(.+)',
            r'Evaluate[:\s]+(.+)',
            r'Solve[:\s]+(.+)',
            r'Compute[:\s]+(.+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, prompt, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return prompt
