"""
Base trace generator interface.

Trace generators convert problems into structured solution traces
that can be verified step-by-step.
"""

from abc import ABC, abstractmethod
from typing import Any

from chuk_math_gym.schemas.problem import Problem
from chuk_math_gym.schemas.trace import Trace


class TraceGenerator(ABC):
    """
    Abstract base class for trace generators.

    Each domain implements its own trace generator that knows how
    to decompose problems into verifiable steps.
    """

    @abstractmethod
    def generate(self, problem: Problem) -> Trace:
        """
        Generate a solution trace for a problem.

        Args:
            problem: The problem to solve

        Returns:
            A Trace containing all solution steps
        """
        pass

    @abstractmethod
    def generate_from_expression(self, expression: str, problem_id: str) -> Trace:
        """
        Generate a trace directly from an expression string.

        Args:
            expression: The mathematical expression
            problem_id: ID to associate with the trace

        Returns:
            A Trace containing all solution steps
        """
        pass
