"""
Arithmetic expression parser.

Tokenizes and parses arithmetic expressions into an AST.
"""

import json
import logging
from decimal import Decimal
from typing import Any, Optional, List

from chuk_math_gym.compiler.lexer.tokenizer import Tokenizer, TokenizationError, Token
from chuk_math_gym.compiler.parser.parser import Parser

logger = logging.getLogger(__name__)


class ArithmeticExpression:
    """Handles tokenization and parsing of arithmetic expressions."""

    def __init__(self, expression: str):
        """Initialize with an arithmetic expression string."""
        self.expression = expression.strip()
        self.tokens: List[Token] = []
        self.ast: Optional[Any] = None

    def tokenize(self) -> List[Token]:
        """
        Tokenize the expression and store the tokens.

        Returns:
            List of tokens.

        Raises:
            ValueError: If tokenization fails.
        """
        try:
            tokenizer = Tokenizer(self.expression)
            self.tokens = tokenizer.tokenize()
            return self.tokens
        except TokenizationError as e:
            logger.warning("Error tokenizing expression: %s", e)
            raise ValueError(f"Error tokenizing expression: {e}") from e

    def parse(self) -> Any:
        """
        Parse the expression into an AST and store it.

        Returns:
            The parsed AST.

        Raises:
            ValueError: If parsing fails.
        """
        try:
            if not self.tokens:
                self.tokenize()

            parser = Parser(self.tokens)
            self.ast = parser.parse()
            return self.ast
        except (ValueError, SyntaxError, TypeError, IndexError) as e:
            logger.warning("Error parsing expression: %s", e)
            raise ValueError(f"Error parsing expression: {e}") from e

    def ast_as_json(self) -> str:
        """
        Convert the AST into a JSON representation.

        Returns:
            JSON string representation of the AST.

        Raises:
            ValueError: If conversion fails.
        """
        if not self.ast:
            self.parse()
        try:
            return json.dumps(self.ast_to_dict(self.ast), indent=2)
        except (TypeError, ValueError) as e:
            raise ValueError(f"Error converting AST to JSON: {e}") from e

    def ast_to_dict(self, ast_node: Any) -> Any:
        """
        Recursively convert the AST into a dictionary.

        Args:
            ast_node: The AST node to convert.

        Returns:
            Dictionary representation of the AST node.
        """
        if isinstance(ast_node, list):
            return [self.ast_to_dict(node) for node in ast_node]
        elif isinstance(ast_node, dict):
            return {key: self.ast_to_dict(value) for key, value in ast_node.items()}
        elif isinstance(ast_node, Decimal):
            return str(ast_node)
        elif isinstance(ast_node, Token):
            return {"type": ast_node.type, "value": ast_node.value, "position": ast_node.position}
        elif hasattr(ast_node, "__dict__"):
            node_dict = {key: self.ast_to_dict(value) for key, value in ast_node.__dict__.items()}
            node_dict["type"] = ast_node.__class__.__name__
            return node_dict
        else:
            return ast_node
