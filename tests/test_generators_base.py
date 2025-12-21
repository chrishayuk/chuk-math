"""Tests for the ProblemGenerator base class."""

import pytest
from typing import Tuple, List, Optional

from chuk_math_gym.generators.base import ProblemGenerator
from chuk_math_gym.schemas.problem import Problem, DifficultyLevel, ToolPolicy, DomainType
from chuk_math_gym.schemas.trace import Trace


class ConcreteProblemGenerator(ProblemGenerator):
    """Concrete implementation of ProblemGenerator for testing."""

    def __init__(self):
        self.generate_count = 0

    def generate(
        self,
        seed: Optional[int] = None,
        difficulty: DifficultyLevel = DifficultyLevel.MEDIUM,
        tool_policy: ToolPolicy = ToolPolicy.ALLOWED,
    ) -> Tuple[Problem, Trace]:
        """Generate a test problem."""
        self.generate_count += 1
        actual_seed = seed if seed is not None else self.generate_count
        problem = Problem(
            id=f"test-{actual_seed}",
            seed=actual_seed,
            domain=DomainType.ARITHMETIC,
            difficulty=difficulty,
            prompt=f"What is 1 + 1? (seed={seed})",
            gold_answer="2",
            tool_policy=tool_policy,
        )
        trace = Trace(problem_id=problem.id, steps=[])
        return problem, trace

    def generate_batch(
        self,
        count: int,
        difficulty: DifficultyLevel = DifficultyLevel.MEDIUM,
        start_seed: Optional[int] = None,
    ) -> List[Tuple[Problem, Trace]]:
        """Generate a batch of test problems."""
        if start_seed is None:
            start_seed = 0
        return [self.generate(start_seed + i, difficulty) for i in range(count)]


class TestProblemGeneratorAbstract:
    """Test abstract nature of ProblemGenerator."""

    def test_cannot_instantiate_abstract_class(self):
        """Test that ProblemGenerator cannot be instantiated directly."""
        with pytest.raises(TypeError):
            ProblemGenerator()


class TestConcreteGenerator:
    """Test concrete implementation of ProblemGenerator."""

    def test_generate_creates_problem(self):
        """Test that generate creates a problem."""
        gen = ConcreteProblemGenerator()
        problem, trace = gen.generate(seed=42)

        assert isinstance(problem, Problem)
        assert isinstance(trace, Trace)
        assert problem.id == "test-42"

    def test_generate_with_difficulty(self):
        """Test generate with specific difficulty."""
        gen = ConcreteProblemGenerator()
        problem, trace = gen.generate(difficulty=DifficultyLevel.HARD)

        assert problem.difficulty == DifficultyLevel.HARD

    def test_generate_with_tool_policy(self):
        """Test generate with specific tool policy."""
        gen = ConcreteProblemGenerator()
        problem, trace = gen.generate(tool_policy=ToolPolicy.FORBIDDEN)

        assert problem.tool_policy == ToolPolicy.FORBIDDEN

    def test_generate_batch(self):
        """Test batch generation."""
        gen = ConcreteProblemGenerator()
        batch = gen.generate_batch(5)

        assert len(batch) == 5
        for problem, trace in batch:
            assert isinstance(problem, Problem)
            assert isinstance(trace, Trace)

    def test_generate_batch_with_start_seed(self):
        """Test batch generation with start seed."""
        gen = ConcreteProblemGenerator()
        batch = gen.generate_batch(3, start_seed=100)

        assert len(batch) == 3
        assert batch[0][0].id == "test-100"
        assert batch[1][0].id == "test-101"
        assert batch[2][0].id == "test-102"

    def test_generate_batch_with_difficulty(self):
        """Test batch generation with difficulty."""
        gen = ConcreteProblemGenerator()
        batch = gen.generate_batch(3, difficulty=DifficultyLevel.EASY)

        for problem, _ in batch:
            assert problem.difficulty == DifficultyLevel.EASY


class TestGenerateIterator:
    """Test generate_iterator method."""

    def test_iterator_yields_problems(self):
        """Test that iterator yields problems."""
        gen = ConcreteProblemGenerator()
        iterator = gen.generate_iterator(start_seed=0)

        problem1, trace1 = next(iterator)
        problem2, trace2 = next(iterator)
        problem3, trace3 = next(iterator)

        assert isinstance(problem1, Problem)
        assert isinstance(problem2, Problem)
        assert isinstance(problem3, Problem)

    def test_iterator_increments_seed(self):
        """Test that iterator increments seed."""
        gen = ConcreteProblemGenerator()
        iterator = gen.generate_iterator(start_seed=10)

        p1, _ = next(iterator)
        p2, _ = next(iterator)
        p3, _ = next(iterator)

        assert "seed=10" in p1.prompt
        assert "seed=11" in p2.prompt
        assert "seed=12" in p3.prompt

    def test_iterator_with_difficulty(self):
        """Test iterator with specific difficulty."""
        gen = ConcreteProblemGenerator()
        iterator = gen.generate_iterator(difficulty=DifficultyLevel.VERY_HARD, start_seed=0)

        problem, _ = next(iterator)
        assert problem.difficulty == DifficultyLevel.VERY_HARD

    def test_iterator_random_start_seed(self):
        """Test iterator with random start seed."""
        gen = ConcreteProblemGenerator()
        iterator = gen.generate_iterator()  # No start_seed

        # Should not raise an error
        problem, _ = next(iterator)
        assert isinstance(problem, Problem)

    def test_iterator_is_infinite(self):
        """Test that iterator is effectively infinite (generates many)."""
        gen = ConcreteProblemGenerator()
        iterator = gen.generate_iterator(start_seed=0)

        # Generate many problems
        for _ in range(100):
            problem, trace = next(iterator)
            assert isinstance(problem, Problem)


class TestValidateDifficulty:
    """Test validate_difficulty method."""

    def test_validate_all_difficulties(self):
        """Test that all difficulties are valid by default."""
        gen = ConcreteProblemGenerator()

        for difficulty in DifficultyLevel:
            assert gen.validate_difficulty(difficulty) is True


class TestGetSupportedDifficulties:
    """Test get_supported_difficulties method."""

    def test_returns_all_difficulties(self):
        """Test that all difficulties are returned by default."""
        gen = ConcreteProblemGenerator()
        supported = gen.get_supported_difficulties()

        assert isinstance(supported, list)
        assert len(supported) == len(list(DifficultyLevel))
        for difficulty in DifficultyLevel:
            assert difficulty in supported


class CustomDifficultyGenerator(ProblemGenerator):
    """Generator with limited difficulty support."""

    SUPPORTED = [DifficultyLevel.EASY, DifficultyLevel.MEDIUM]

    def generate(
        self,
        seed: Optional[int] = None,
        difficulty: DifficultyLevel = DifficultyLevel.MEDIUM,
        tool_policy: ToolPolicy = ToolPolicy.ALLOWED,
    ) -> Tuple[Problem, Trace]:
        actual_seed = seed if seed is not None else 1
        problem = Problem(
            id="test",
            seed=actual_seed,
            domain=DomainType.ARITHMETIC,
            difficulty=difficulty,
            prompt="test",
            gold_answer="1",
        )
        return problem, Trace(problem_id="test", steps=[])

    def generate_batch(
        self,
        count: int,
        difficulty: DifficultyLevel = DifficultyLevel.MEDIUM,
        start_seed: Optional[int] = None,
    ) -> List[Tuple[Problem, Trace]]:
        return [self.generate(difficulty=difficulty) for _ in range(count)]

    def validate_difficulty(self, difficulty: DifficultyLevel) -> bool:
        return difficulty in self.SUPPORTED

    def get_supported_difficulties(self) -> List[DifficultyLevel]:
        return self.SUPPORTED


class TestCustomDifficultyGenerator:
    """Test generator with custom difficulty support."""

    def test_validate_supported_difficulty(self):
        """Test validating a supported difficulty."""
        gen = CustomDifficultyGenerator()
        assert gen.validate_difficulty(DifficultyLevel.EASY) is True
        assert gen.validate_difficulty(DifficultyLevel.MEDIUM) is True

    def test_validate_unsupported_difficulty(self):
        """Test validating an unsupported difficulty."""
        gen = CustomDifficultyGenerator()
        assert gen.validate_difficulty(DifficultyLevel.HARD) is False
        assert gen.validate_difficulty(DifficultyLevel.VERY_HARD) is False

    def test_get_supported_returns_limited(self):
        """Test get_supported_difficulties returns limited list."""
        gen = CustomDifficultyGenerator()
        supported = gen.get_supported_difficulties()

        assert len(supported) == 2
        assert DifficultyLevel.EASY in supported
        assert DifficultyLevel.MEDIUM in supported
        assert DifficultyLevel.HARD not in supported
