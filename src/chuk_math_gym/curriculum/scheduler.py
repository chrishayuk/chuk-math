"""
Curriculum scheduler for adaptive training.

The scheduler manages problem generation with adaptive difficulty,
tracking performance and adjusting the curriculum accordingly.
"""

from typing import Optional, Tuple, List, Dict, Any
from dataclasses import dataclass, field
import random
import json
from pathlib import Path

from chuk_math_gym.schemas.problem import Problem, DomainType, DifficultyLevel, ToolPolicy
from chuk_math_gym.schemas.trace import Trace
from chuk_math_gym.schemas.verification import VerificationResult
from chuk_math_gym.curriculum.strategies import (
    CurriculumStrategy,
    PerformanceBasedStrategy,
    PerformanceMetrics,
)


@dataclass
class ProgressTracker:
    """
    Tracks learner progress across domains and difficulties.

    Maintains performance metrics and history for curriculum decisions.
    """

    # Per-domain metrics
    domain_metrics: Dict[DomainType, PerformanceMetrics] = field(default_factory=dict)

    # Current difficulty per domain
    current_difficulties: Dict[DomainType, DifficultyLevel] = field(default_factory=dict)

    # Problem history
    problem_history: List[Dict[str, Any]] = field(default_factory=list)
    max_history: int = 1000

    # Session stats
    session_problems: int = 0
    session_correct: int = 0
    session_score: float = 0.0

    def record_result(
        self,
        problem: Problem,
        result: VerificationResult,
    ):
        """Record the result of a problem attempt."""
        domain = problem.domain
        difficulty = problem.difficulty

        # Get or create domain metrics
        if domain not in self.domain_metrics:
            self.domain_metrics[domain] = PerformanceMetrics()

        metrics = self.domain_metrics[domain]
        metrics.record_result(difficulty, result.score, result.correct)

        # Update session stats
        self.session_problems += 1
        if result.correct:
            self.session_correct += 1
        self.session_score += result.score

        # Record in history
        self.problem_history.append(
            {
                "problem_id": problem.id,
                "domain": domain.value,
                "difficulty": difficulty.value,
                "correct": result.correct,
                "score": result.score,
                "error_type": result.error_type.value if result.error_type else None,
            }
        )

        # Trim history if needed
        if len(self.problem_history) > self.max_history:
            self.problem_history = self.problem_history[-self.max_history :]

    def get_metrics(self, domain: DomainType) -> PerformanceMetrics:
        """Get metrics for a domain."""
        if domain not in self.domain_metrics:
            self.domain_metrics[domain] = PerformanceMetrics()
        return self.domain_metrics[domain]

    def get_current_difficulty(self, domain: DomainType) -> DifficultyLevel:
        """Get current difficulty for a domain."""
        return self.current_difficulties.get(domain, DifficultyLevel.MEDIUM)

    def set_difficulty(self, domain: DomainType, difficulty: DifficultyLevel):
        """Set difficulty for a domain."""
        self.current_difficulties[domain] = difficulty

    @property
    def session_accuracy(self) -> float:
        """Get session accuracy."""
        if self.session_problems == 0:
            return 0.0
        return self.session_correct / self.session_problems

    def get_weakest_domain(self) -> Optional[DomainType]:
        """Find the domain with lowest accuracy."""
        weakest = None
        lowest_acc = 1.0

        for domain, metrics in self.domain_metrics.items():
            if metrics.total_problems > 0 and metrics.accuracy < lowest_acc:
                lowest_acc = metrics.accuracy
                weakest = domain

        return weakest

    def get_strongest_domain(self) -> Optional[DomainType]:
        """Find the domain with highest accuracy."""
        strongest = None
        highest_acc = 0.0

        for domain, metrics in self.domain_metrics.items():
            if metrics.total_problems > 0 and metrics.accuracy > highest_acc:
                highest_acc = metrics.accuracy
                strongest = domain

        return strongest

    def save(self, path: str):
        """Save progress to file."""
        data = {
            "domain_metrics": {
                d.value: {
                    "total": m.total_problems,
                    "correct": m.correct_count,
                    "score": m.total_score,
                }
                for d, m in self.domain_metrics.items()
            },
            "current_difficulties": {
                d.value: diff.value for d, diff in self.current_difficulties.items()
            },
            "session_problems": self.session_problems,
            "session_correct": self.session_correct,
            "session_score": self.session_score,
        }
        Path(path).write_text(json.dumps(data, indent=2))

    @classmethod
    def load(cls, path: str) -> "ProgressTracker":
        """Load progress from file."""
        data = json.loads(Path(path).read_text())

        tracker = cls()

        # Restore domain metrics
        for domain_str, stats in data.get("domain_metrics", {}).items():
            domain = DomainType(domain_str)
            metrics = PerformanceMetrics()
            metrics.total_problems = stats["total"]
            metrics.correct_count = stats["correct"]
            metrics.total_score = stats["score"]
            tracker.domain_metrics[domain] = metrics

        # Restore difficulties
        for domain_str, diff_str in data.get("current_difficulties", {}).items():
            domain = DomainType(domain_str)
            difficulty = DifficultyLevel(diff_str)
            tracker.current_difficulties[domain] = difficulty

        tracker.session_problems = data.get("session_problems", 0)
        tracker.session_correct = data.get("session_correct", 0)
        tracker.session_score = data.get("session_score", 0.0)

        return tracker


class CurriculumScheduler:
    """
    Schedules problems with adaptive difficulty.

    Uses a curriculum strategy to adjust difficulty based on
    learner performance.
    """

    def __init__(
        self,
        strategy: Optional[CurriculumStrategy] = None,
        initial_difficulty: DifficultyLevel = DifficultyLevel.MEDIUM,
        domains: Optional[List[DomainType]] = None,
    ):
        """
        Initialize the curriculum scheduler.

        Args:
            strategy: Curriculum strategy to use (default: PerformanceBasedStrategy)
            initial_difficulty: Starting difficulty level
            domains: List of domains to include (default: all)
        """
        self.strategy = strategy or PerformanceBasedStrategy()
        self.initial_difficulty = initial_difficulty
        self.domains = domains or list(DomainType)

        self.tracker = ProgressTracker()
        self._generators: Dict[DomainType, Any] = {}
        self._seed_counter = random.randint(0, 2**31 - 1)

    def _get_generator(self, domain: DomainType):
        """Get or create a generator for a domain."""
        if domain not in self._generators:
            if domain == DomainType.ARITHMETIC:
                from chuk_math_gym.domains.arithmetic import ArithmeticGenerator

                self._generators[domain] = ArithmeticGenerator()
            elif domain == DomainType.FRACTIONS:
                from chuk_math_gym.domains.fractions import FractionsGenerator

                self._generators[domain] = FractionsGenerator()
            elif domain == DomainType.LINEAR_EQUATIONS:
                from chuk_math_gym.domains.linear_equations import LinearEquationsGenerator

                self._generators[domain] = LinearEquationsGenerator()
            else:
                raise ValueError(f"Unsupported domain: {domain}")

        return self._generators[domain]

    def next_problem(
        self,
        domain: Optional[DomainType] = None,
        tool_policy: ToolPolicy = ToolPolicy.ALLOWED,
    ) -> Tuple[Problem, Trace]:
        """
        Get the next problem based on curriculum.

        Args:
            domain: Specific domain (or None for automatic selection)
            tool_policy: Tool usage policy

        Returns:
            Tuple of (Problem, Trace)
        """
        # Select domain
        if domain is None:
            domain = self._select_domain()

        # Get current difficulty
        difficulty = self.tracker.get_current_difficulty(domain)
        if difficulty is None:
            difficulty = self.initial_difficulty
            self.tracker.set_difficulty(domain, difficulty)

        # Generate problem
        generator = self._get_generator(domain)
        self._seed_counter += 1

        problem, trace = generator.generate(
            seed=self._seed_counter,
            difficulty=difficulty,
            tool_policy=tool_policy,
        )

        return problem, trace

    def record_result(
        self,
        problem: Problem,
        result: VerificationResult,
    ):
        """
        Record a problem result and update curriculum.

        Args:
            problem: The problem that was attempted
            result: The verification result
        """
        # Record in tracker
        self.tracker.record_result(problem, result)

        # Update strategy (for EMA-based strategies)
        if hasattr(self.strategy, "update_ema"):
            self.strategy.update_ema(problem.difficulty, result.score)

        # Check if difficulty should change
        metrics = self.tracker.get_metrics(problem.domain)
        current_diff = self.tracker.get_current_difficulty(problem.domain)

        new_diff = self.strategy.select_difficulty(metrics, current_diff, problem.domain)

        if new_diff != current_diff:
            self.tracker.set_difficulty(problem.domain, new_diff)

    def _select_domain(self) -> DomainType:
        """Select a domain based on performance."""
        # 70% chance: focus on weakest domain
        # 30% chance: random domain
        if random.random() < 0.7:
            weakest = self.tracker.get_weakest_domain()
            if weakest:
                return weakest

        return random.choice(self.domains)

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of current curriculum state."""
        summary = {
            "session": {
                "problems": self.tracker.session_problems,
                "accuracy": self.tracker.session_accuracy,
                "score": self.tracker.session_score,
            },
            "domains": {},
        }

        domains_dict: Dict[str, Any] = {}
        for domain in self.domains:
            metrics = self.tracker.get_metrics(domain)
            domains_dict[domain.value] = {
                "difficulty": self.tracker.get_current_difficulty(domain).value,
                "problems": metrics.total_problems,
                "accuracy": metrics.accuracy,
                "recent_accuracy": metrics.recent_accuracy,
            }
        summary["domains"] = domains_dict

        return summary


class AdaptiveCurriculumScheduler(CurriculumScheduler):
    """
    Enhanced curriculum scheduler with additional features.

    Includes:
    - Domain balancing
    - Spaced repetition for difficult problems
    - Mastery tracking
    """

    def __init__(
        self,
        strategy: Optional[CurriculumStrategy] = None,
        initial_difficulty: DifficultyLevel = DifficultyLevel.MEDIUM,
        domains: Optional[List[DomainType]] = None,
        mastery_threshold: float = 0.9,
        repetition_factor: float = 0.2,
    ):
        """
        Initialize adaptive scheduler.

        Args:
            strategy: Curriculum strategy
            initial_difficulty: Starting difficulty
            domains: Domains to include
            mastery_threshold: Accuracy threshold for mastery
            repetition_factor: Probability of repeating difficult problems
        """
        super().__init__(strategy, initial_difficulty, domains)
        self.mastery_threshold = mastery_threshold
        self.repetition_factor = repetition_factor

        self._difficult_problems: List[Tuple[Problem, Optional[Trace]]] = []
        self._max_difficult = 50

    def next_problem(
        self,
        domain: Optional[DomainType] = None,
        tool_policy: ToolPolicy = ToolPolicy.ALLOWED,
    ) -> Tuple[Problem, Trace]:
        """Get next problem with spaced repetition."""
        # Occasionally repeat a difficult problem
        if self._difficult_problems and random.random() < self.repetition_factor:
            problem, _trace = random.choice(self._difficult_problems)
            # Regenerate with new seed to vary slightly
            generator = self._get_generator(problem.domain)
            result: Tuple[Problem, Trace] = generator.generate(
                seed=self._seed_counter,
                difficulty=problem.difficulty,
                tool_policy=tool_policy,
            )
            return result

        return super().next_problem(domain, tool_policy)

    def record_result(
        self,
        problem: Problem,
        result: VerificationResult,
    ):
        """Record result with spaced repetition tracking."""
        super().record_result(problem, result)

        # Track difficult problems for repetition
        if not result.correct or result.score < 0.5:
            # Add to difficult problems
            self._difficult_problems.append((problem, None))
            if len(self._difficult_problems) > self._max_difficult:
                self._difficult_problems.pop(0)
        else:
            # Remove from difficult if mastered
            self._difficult_problems = [
                (p, t) for p, t in self._difficult_problems if p.id != problem.id
            ]

    def is_mastered(self, domain: DomainType) -> bool:
        """Check if a domain is mastered at current difficulty."""
        metrics = self.tracker.get_metrics(domain)
        difficulty = self.tracker.get_current_difficulty(domain)
        return metrics.get_difficulty_accuracy(difficulty) >= self.mastery_threshold

    def get_mastery_status(self) -> Dict[str, bool]:
        """Get mastery status for all domains."""
        return {domain.value: self.is_mastered(domain) for domain in self.domains}
