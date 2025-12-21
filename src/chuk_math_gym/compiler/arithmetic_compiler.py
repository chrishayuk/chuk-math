"""
Arithmetic expression compiler.

Parses arithmetic expressions and generates instruction outputs.
"""

import logging
from typing import Optional, Any

from chuk_math_gym.compiler.instructions.math_problem_instruction import MATHProblemInstruction
from chuk_math_gym.compiler.parser.arithmetic_expression import ArithmeticExpression, TokenizationError
from chuk_math_gym.compiler.instructions.infix_expression_calculator_instruction import InfixExpressionCalculatorInstruction

logger = logging.getLogger(__name__)


class ArithmeticCompiler:
    """Compiles arithmetic expressions into instruction outputs."""

    def __init__(self, expression: str):
        """Initialize the compiler with an expression."""
        self.expression = expression
        self.arithmetic_expression = ArithmeticExpression(expression)
        self.ast: Optional[Any] = None
        self.json_ast: Optional[dict] = None
        self.tokens: Optional[list] = None
        self.instruction: Optional[InfixExpressionCalculatorInstruction] = None

    def parse_expression(self) -> bool:
        """
        Parse the expression into an AST and its JSON representation.

        Returns:
            True if parsing succeeded, False otherwise.
        """
        try:
            self.tokens = self.arithmetic_expression.tokenize()
            self.ast = self.arithmetic_expression.parse()
            self.json_ast = self.arithmetic_expression.ast_as_json()
            return True
        except TokenizationError as e:
            logger.warning("Tokenization error: %s", e)
            self._clear_parse_state()
            return False
        except (ValueError, SyntaxError, TypeError) as e:
            logger.warning("Parse error: %s", e)
            self._clear_parse_state()
            return False

    def _clear_parse_state(self) -> None:
        """Clear parsing state on error."""
        self.tokens = []
        self.ast = None
        self.json_ast = None

    def generate_instruction(self, llm: Optional[str] = None) -> bool:
        """
        Generate instruction outputs based on the AST and tokens.

        Args:
            llm: Optional language model name for LLM-based generation.

        Returns:
            True if instruction generation succeeded, False otherwise.
        """
        if not self.ast or not self.tokens:
            logger.warning("No AST or tokens available to generate instruction.")
            self.instruction = None
            return False

        try:
            self.instruction = InfixExpressionCalculatorInstruction(
                self.json_ast, self.tokens, llm=llm
            )
            return True
        except (ValueError, TypeError, KeyError) as e:
            logger.warning("Error during instruction initialization: %s", e)
            self.instruction = None
            return False

    def compile(self) -> dict:
        """
        Full compilation process: parse, generate instructions, and emit outputs.

        Returns:
            Instruction output dictionary, or empty dict on failure.
        """
        self.parse_expression()
        self.generate_instruction(None)

        if self.instruction:
            return self.instruction.emit_instruction()
        return {}
