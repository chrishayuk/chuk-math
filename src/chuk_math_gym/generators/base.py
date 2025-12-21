"""
Abstract base class for problem generators.

All domain-specific generators should inherit from ProblemGenerator
to ensure a consistent interface across the system.
"""

from abc import ABC, abstractmethod
from typing import Optional, Tuple, List, Iterator

from chuk_math_gym.schemas.problem import Problem, DifficultyLevel, ToolPolicy
from chuk_math_gym.schemas.trace import Trace


class ProblemGenerator(ABC):
    """
    Abstract base class for problem generators.

    All domain generators (ArithmeticGenerator, FractionsGenerator, etc.)
    should inherit from this class to ensure interface consistency.

    Example:
        class MyDomainGenerator(ProblemGenerator):
            def generate(self, seed, difficulty, tool_policy):
                # Generate problem and trace
                return problem, trace

            def generate_batch(self, count, difficulty, start_seed):
                return [self.generate(start_seed + i, difficulty) for i in range(count)]
    """

    @abstractmethod
    def generate(
        self,
        seed: Optional[int] = None,
        difficulty: DifficultyLevel = DifficultyLevel.MEDIUM,
        tool_policy: ToolPolicy = ToolPolicy.ALLOWED,
    ) -> Tuple[Problem, Trace]:
        """
        Generate a single problem with its solution trace.

        Args:
            seed: Random seed for reproducibility. If None, uses random seed.
            difficulty: Difficulty level for the problem.
            tool_policy: Policy for tool usage in solving the problem.

        Returns:
            Tuple of (Problem, Trace) where Problem contains the question
            and Trace contains the step-by-step solution.

        Raises:
            ValueError: If difficulty is not supported by this generator.
            ZeroDivisionError: If generated expression contains division by zero.
        """
        pass

    @abstractmethod
    def generate_batch(
        self,
        count: int,
        difficulty: DifficultyLevel = DifficultyLevel.MEDIUM,
        start_seed: Optional[int] = None,
    ) -> List[Tuple[Problem, Trace]]:
        """
        Generate a batch of problems.

        Args:
            count: Number of problems to generate.
            difficulty: Difficulty level for all problems.
            start_seed: Starting seed. Problems will use seeds
                       start_seed, start_seed+1, ..., start_seed+count-1.

        Returns:
            List of (Problem, Trace) tuples.
        """
        pass

    def generate_iterator(
        self,
        difficulty: DifficultyLevel = DifficultyLevel.MEDIUM,
        start_seed: Optional[int] = None,
    ) -> Iterator[Tuple[Problem, Trace]]:
        """
        Generate an infinite iterator of problems.

        Useful for training loops where you want continuous problem generation.

        Args:
            difficulty: Difficulty level for problems.
            start_seed: Starting seed. If None, uses random starting point.

        Yields:
            (Problem, Trace) tuples indefinitely.
        """
        import random

        if start_seed is None:
            start_seed = random.randint(0, 2**31 - 1)

        seed = start_seed
        while True:
            yield self.generate(seed=seed, difficulty=difficulty)
            seed = (seed + 1) % (2**31)  # Wrap around to avoid overflow

    def validate_difficulty(self, difficulty: DifficultyLevel) -> bool:
        """
        Check if this generator supports the given difficulty level.

        Override in subclasses if certain difficulty levels are not supported.

        Args:
            difficulty: Difficulty level to check.

        Returns:
            True if supported, False otherwise.
        """
        return True

    def get_supported_difficulties(self) -> List[DifficultyLevel]:
        """
        Get list of difficulty levels supported by this generator.

        Override in subclasses if not all difficulties are supported.

        Returns:
            List of supported DifficultyLevel values.
        """
        return list(DifficultyLevel)
