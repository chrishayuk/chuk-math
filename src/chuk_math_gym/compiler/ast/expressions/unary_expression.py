"""Unary expression AST node."""

import logging

from .expression import Expression

logger = logging.getLogger(__name__)


class UnaryExpression(Expression):
    """Represents a unary expression (e.g., -x, +5)."""

    def __init__(self, operator, operand):
        self.operator = operator
        self.operand = operand

    def __eq__(self, other):
        if isinstance(other, UnaryExpression):
            if self.operator != other.operator:
                logger.debug("Operator mismatch: %s != %s", self.operator, other.operator)
            if self.operand != other.operand:
                logger.debug("Operand mismatch: %s != %s", self.operand, other.operand)
            return self.operator == other.operator and self.operand == other.operand
        return False

    def __repr__(self):
        return f"UnaryExpression(operator={repr(self.operator)}, operand={repr(self.operand)})"

    def to_dict(self):
        """Convert unary expression to dictionary, handles recursion."""
        return {
            "type": "UnaryExpression",
            "operator": self.operator.value
            if hasattr(self.operator, "value")
            else str(self.operator),
            "operand": self.operand.to_dict()
            if hasattr(self.operand, "to_dict")
            else str(self.operand),
        }
