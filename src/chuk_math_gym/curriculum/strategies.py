"""
Curriculum strategies for adaptive difficulty selection.

Strategies determine how to adjust difficulty based on learner performance.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from enum import Enum

from chuk_math_gym.schemas.problem import DomainType, DifficultyLevel


@dataclass
class PerformanceMetrics:
    """Metrics tracking learner performance."""

    total_problems: int = 0
    correct_count: int = 0
    total_score: float = 0.0

    # Per-difficulty stats
    difficulty_stats: Dict[DifficultyLevel, Dict[str, float]] = field(default_factory=dict)

    # Recent performance (sliding window)
    recent_scores: List[float] = field(default_factory=list)
    window_size: int = 10

    @property
    def accuracy(self) -> float:
        """Overall accuracy."""
        if self.total_problems == 0:
            return 0.0
        return self.correct_count / self.total_problems

    @property
    def average_score(self) -> float:
        """Average score across all problems."""
        if self.total_problems == 0:
            return 0.0
        return self.total_score / self.total_problems

    @property
    def recent_accuracy(self) -> float:
        """Accuracy over recent problems."""
        if not self.recent_scores:
            return 0.0
        return sum(self.recent_scores) / len(self.recent_scores)

    def record_result(self, difficulty: DifficultyLevel, score: float, correct: bool):
        """Record a problem result."""
        self.total_problems += 1
        self.total_score += score
        if correct:
            self.correct_count += 1

        # Update per-difficulty stats
        if difficulty not in self.difficulty_stats:
            self.difficulty_stats[difficulty] = {
                "total": 0,
                "correct": 0,
                "total_score": 0.0,
            }
        stats = self.difficulty_stats[difficulty]
        stats["total"] += 1
        stats["correct"] += 1 if correct else 0
        stats["total_score"] += score

        # Update sliding window
        self.recent_scores.append(score)
        if len(self.recent_scores) > self.window_size:
            self.recent_scores.pop(0)

    def get_difficulty_accuracy(self, difficulty: DifficultyLevel) -> float:
        """Get accuracy for a specific difficulty."""
        stats = self.difficulty_stats.get(difficulty)
        if not stats or stats["total"] == 0:
            return 0.0
        return stats["correct"] / stats["total"]


class CurriculumStrategy(ABC):
    """
    Abstract base class for curriculum strategies.

    Strategies determine how to select difficulty based on performance.
    """

    @abstractmethod
    def select_difficulty(
        self,
        metrics: PerformanceMetrics,
        current_difficulty: DifficultyLevel,
        domain: Optional[DomainType] = None,
    ) -> DifficultyLevel:
        """
        Select the next difficulty level.

        Args:
            metrics: Current performance metrics
            current_difficulty: Current difficulty level
            domain: Optional domain context

        Returns:
            Selected difficulty level
        """
        pass

    @abstractmethod
    def should_advance(
        self,
        metrics: PerformanceMetrics,
        current_difficulty: DifficultyLevel,
    ) -> bool:
        """Check if learner should advance to higher difficulty."""
        pass

    @abstractmethod
    def should_retreat(
        self,
        metrics: PerformanceMetrics,
        current_difficulty: DifficultyLevel,
    ) -> bool:
        """Check if learner should retreat to lower difficulty."""
        pass


class LinearStrategy(CurriculumStrategy):
    """
    Simple linear progression through difficulty levels.

    Advances after N correct answers, retreats after M wrong answers.
    """

    def __init__(
        self,
        correct_to_advance: int = 5,
        wrong_to_retreat: int = 3,
    ):
        """
        Initialize linear strategy.

        Args:
            correct_to_advance: Consecutive correct answers to advance
            wrong_to_retreat: Consecutive wrong answers to retreat
        """
        self.correct_to_advance = correct_to_advance
        self.wrong_to_retreat = wrong_to_retreat
        self._consecutive_correct = 0
        self._consecutive_wrong = 0

    def select_difficulty(
        self,
        metrics: PerformanceMetrics,
        current_difficulty: DifficultyLevel,
        domain: Optional[DomainType] = None,
    ) -> DifficultyLevel:
        """Select next difficulty based on consecutive results."""
        if self.should_advance(metrics, current_difficulty):
            return self._next_level(current_difficulty)
        if self.should_retreat(metrics, current_difficulty):
            return self._prev_level(current_difficulty)
        return current_difficulty

    def should_advance(
        self,
        metrics: PerformanceMetrics,
        current_difficulty: DifficultyLevel,
    ) -> bool:
        """Advance after consecutive correct answers."""
        if not metrics.recent_scores:
            return False

        # Check last N scores
        recent = metrics.recent_scores[-self.correct_to_advance:]
        if len(recent) < self.correct_to_advance:
            return False

        return all(s >= 0.9 for s in recent)

    def should_retreat(
        self,
        metrics: PerformanceMetrics,
        current_difficulty: DifficultyLevel,
    ) -> bool:
        """Retreat after consecutive wrong answers."""
        if not metrics.recent_scores:
            return False

        recent = metrics.recent_scores[-self.wrong_to_retreat:]
        if len(recent) < self.wrong_to_retreat:
            return False

        return all(s < 0.5 for s in recent)

    def _next_level(self, current: DifficultyLevel) -> DifficultyLevel:
        """Get next difficulty level."""
        levels = list(DifficultyLevel)
        idx = levels.index(current)
        if idx < len(levels) - 1:
            return levels[idx + 1]
        return current

    def _prev_level(self, current: DifficultyLevel) -> DifficultyLevel:
        """Get previous difficulty level."""
        levels = list(DifficultyLevel)
        idx = levels.index(current)
        if idx > 0:
            return levels[idx - 1]
        return current


class PerformanceBasedStrategy(CurriculumStrategy):
    """
    Performance-based difficulty selection.

    Targets a specific accuracy range and adjusts difficulty
    to keep the learner in the "zone of proximal development".
    """

    def __init__(
        self,
        target_accuracy: float = 0.75,
        tolerance: float = 0.1,
        min_problems: int = 5,
    ):
        """
        Initialize performance-based strategy.

        Args:
            target_accuracy: Target accuracy to maintain (0.0 to 1.0)
            tolerance: Acceptable deviation from target
            min_problems: Minimum problems before adjusting
        """
        self.target_accuracy = target_accuracy
        self.tolerance = tolerance
        self.min_problems = min_problems

    def select_difficulty(
        self,
        metrics: PerformanceMetrics,
        current_difficulty: DifficultyLevel,
        domain: Optional[DomainType] = None,
    ) -> DifficultyLevel:
        """Select difficulty to maintain target accuracy."""
        if self.should_advance(metrics, current_difficulty):
            return self._next_level(current_difficulty)
        if self.should_retreat(metrics, current_difficulty):
            return self._prev_level(current_difficulty)
        return current_difficulty

    def should_advance(
        self,
        metrics: PerformanceMetrics,
        current_difficulty: DifficultyLevel,
    ) -> bool:
        """Advance if accuracy is too high."""
        accuracy = metrics.get_difficulty_accuracy(current_difficulty)
        stats = metrics.difficulty_stats.get(current_difficulty, {})

        if stats.get("total", 0) < self.min_problems:
            return False

        return accuracy > self.target_accuracy + self.tolerance

    def should_retreat(
        self,
        metrics: PerformanceMetrics,
        current_difficulty: DifficultyLevel,
    ) -> bool:
        """Retreat if accuracy is too low."""
        accuracy = metrics.get_difficulty_accuracy(current_difficulty)
        stats = metrics.difficulty_stats.get(current_difficulty, {})

        if stats.get("total", 0) < self.min_problems:
            return False

        return accuracy < self.target_accuracy - self.tolerance

    def _next_level(self, current: DifficultyLevel) -> DifficultyLevel:
        levels = list(DifficultyLevel)
        idx = levels.index(current)
        if idx < len(levels) - 1:
            return levels[idx + 1]
        return current

    def _prev_level(self, current: DifficultyLevel) -> DifficultyLevel:
        levels = list(DifficultyLevel)
        idx = levels.index(current)
        if idx > 0:
            return levels[idx - 1]
        return current


class SelfPacedStrategy(CurriculumStrategy):
    """
    Self-paced learning with momentum.

    Uses exponential moving average of performance to make
    smooth transitions between difficulty levels.
    """

    def __init__(
        self,
        alpha: float = 0.3,  # EMA smoothing factor
        advance_threshold: float = 0.85,
        retreat_threshold: float = 0.5,
    ):
        """
        Initialize self-paced strategy.

        Args:
            alpha: Smoothing factor for EMA (higher = more reactive)
            advance_threshold: EMA threshold to advance
            retreat_threshold: EMA threshold to retreat
        """
        self.alpha = alpha
        self.advance_threshold = advance_threshold
        self.retreat_threshold = retreat_threshold
        self._ema_scores: Dict[DifficultyLevel, float] = {}

    def select_difficulty(
        self,
        metrics: PerformanceMetrics,
        current_difficulty: DifficultyLevel,
        domain: Optional[DomainType] = None,
    ) -> DifficultyLevel:
        """Select difficulty based on EMA of scores."""
        if self.should_advance(metrics, current_difficulty):
            return self._next_level(current_difficulty)
        if self.should_retreat(metrics, current_difficulty):
            return self._prev_level(current_difficulty)
        return current_difficulty

    def update_ema(self, difficulty: DifficultyLevel, score: float):
        """Update EMA for a difficulty level."""
        current = self._ema_scores.get(difficulty, 0.5)
        self._ema_scores[difficulty] = self.alpha * score + (1 - self.alpha) * current

    def should_advance(
        self,
        metrics: PerformanceMetrics,
        current_difficulty: DifficultyLevel,
    ) -> bool:
        """Advance if EMA is above threshold."""
        ema = self._ema_scores.get(current_difficulty, 0.5)
        return ema >= self.advance_threshold

    def should_retreat(
        self,
        metrics: PerformanceMetrics,
        current_difficulty: DifficultyLevel,
    ) -> bool:
        """Retreat if EMA is below threshold."""
        ema = self._ema_scores.get(current_difficulty, 0.5)
        return ema < self.retreat_threshold

    def _next_level(self, current: DifficultyLevel) -> DifficultyLevel:
        levels = list(DifficultyLevel)
        idx = levels.index(current)
        if idx < len(levels) - 1:
            return levels[idx + 1]
        return current

    def _prev_level(self, current: DifficultyLevel) -> DifficultyLevel:
        levels = list(DifficultyLevel)
        idx = levels.index(current)
        if idx > 0:
            return levels[idx - 1]
        return current
