"""Tests for the curriculum scheduler and strategies."""

import pytest
from unittest.mock import MagicMock

from chuk_math_gym.schemas.problem import DifficultyLevel, DomainType, ToolPolicy
from chuk_math_gym.schemas.verification import VerificationResult
from chuk_math_gym.curriculum import (
    CurriculumScheduler,
    AdaptiveCurriculumScheduler,
    ProgressTracker,
    CurriculumStrategy,
    LinearStrategy,
    PerformanceBasedStrategy,
    SelfPacedStrategy,
)
from chuk_math_gym.curriculum.strategies import PerformanceMetrics


class TestPerformanceMetrics:
    """Tests for PerformanceMetrics."""

    def test_initial_state(self):
        """Test initial metrics state."""
        metrics = PerformanceMetrics()

        assert metrics.total_problems == 0
        assert metrics.correct_count == 0
        assert metrics.accuracy == 0.0
        assert metrics.average_score == 0.0
        assert metrics.recent_accuracy == 0.0

    def test_record_result(self):
        """Test recording a result."""
        metrics = PerformanceMetrics()

        metrics.record_result(DifficultyLevel.MEDIUM, 1.0, True)

        assert metrics.total_problems == 1
        assert metrics.correct_count == 1
        assert metrics.accuracy == 1.0
        assert metrics.total_score == 1.0

    def test_accuracy_calculation(self):
        """Test accuracy calculation."""
        metrics = PerformanceMetrics()

        # 3 correct, 1 wrong
        metrics.record_result(DifficultyLevel.MEDIUM, 1.0, True)
        metrics.record_result(DifficultyLevel.MEDIUM, 1.0, True)
        metrics.record_result(DifficultyLevel.MEDIUM, 1.0, True)
        metrics.record_result(DifficultyLevel.MEDIUM, 0.0, False)

        assert metrics.accuracy == 0.75
        assert metrics.total_problems == 4

    def test_per_difficulty_stats(self):
        """Test per-difficulty statistics."""
        metrics = PerformanceMetrics()

        # Easy: 2 correct
        metrics.record_result(DifficultyLevel.EASY, 1.0, True)
        metrics.record_result(DifficultyLevel.EASY, 1.0, True)

        # Medium: 1 correct, 1 wrong
        metrics.record_result(DifficultyLevel.MEDIUM, 1.0, True)
        metrics.record_result(DifficultyLevel.MEDIUM, 0.0, False)

        assert metrics.get_difficulty_accuracy(DifficultyLevel.EASY) == 1.0
        assert metrics.get_difficulty_accuracy(DifficultyLevel.MEDIUM) == 0.5

    def test_sliding_window(self):
        """Test sliding window for recent scores."""
        metrics = PerformanceMetrics(window_size=5)

        # Add more than window size
        for i in range(10):
            score = 1.0 if i >= 5 else 0.0
            metrics.record_result(DifficultyLevel.MEDIUM, score, score > 0.5)

        # Recent should only include last 5 (all 1.0)
        assert len(metrics.recent_scores) == 5
        assert metrics.recent_accuracy == 1.0


class TestLinearStrategy:
    """Tests for LinearStrategy."""

    def test_should_advance(self):
        """Test advancement condition."""
        strategy = LinearStrategy(correct_to_advance=3, wrong_to_retreat=2)
        metrics = PerformanceMetrics()

        # Not enough correct yet
        metrics.record_result(DifficultyLevel.MEDIUM, 1.0, True)
        metrics.record_result(DifficultyLevel.MEDIUM, 1.0, True)
        assert not strategy.should_advance(metrics, DifficultyLevel.MEDIUM)

        # Now should advance
        metrics.record_result(DifficultyLevel.MEDIUM, 1.0, True)
        assert strategy.should_advance(metrics, DifficultyLevel.MEDIUM)

    def test_should_retreat(self):
        """Test retreat condition."""
        strategy = LinearStrategy(correct_to_advance=3, wrong_to_retreat=2)
        metrics = PerformanceMetrics()

        # One wrong
        metrics.record_result(DifficultyLevel.MEDIUM, 0.0, False)
        assert not strategy.should_retreat(metrics, DifficultyLevel.MEDIUM)

        # Two wrong - should retreat
        metrics.record_result(DifficultyLevel.MEDIUM, 0.0, False)
        assert strategy.should_retreat(metrics, DifficultyLevel.MEDIUM)

    def test_select_difficulty_advance(self):
        """Test difficulty selection when advancing."""
        strategy = LinearStrategy(correct_to_advance=2)
        metrics = PerformanceMetrics()

        # Get enough correct answers
        metrics.record_result(DifficultyLevel.MEDIUM, 1.0, True)
        metrics.record_result(DifficultyLevel.MEDIUM, 1.0, True)

        new_diff = strategy.select_difficulty(metrics, DifficultyLevel.MEDIUM)
        assert new_diff == DifficultyLevel.HARD

    def test_select_difficulty_retreat(self):
        """Test difficulty selection when retreating."""
        strategy = LinearStrategy(wrong_to_retreat=2)
        metrics = PerformanceMetrics()

        # Get wrong answers (score < 0.5 triggers retreat)
        metrics.record_result(DifficultyLevel.MEDIUM, 0.3, False)
        metrics.record_result(DifficultyLevel.MEDIUM, 0.3, False)

        new_diff = strategy.select_difficulty(metrics, DifficultyLevel.MEDIUM)
        # MEDIUM -> PRETTY_EASY (one step down)
        assert new_diff == DifficultyLevel.PRETTY_EASY

    def test_no_advance_beyond_max(self):
        """Test that can't advance beyond max difficulty."""
        strategy = LinearStrategy(correct_to_advance=1)
        metrics = PerformanceMetrics()

        metrics.record_result(DifficultyLevel.VERY_HARD, 1.0, True)

        new_diff = strategy.select_difficulty(metrics, DifficultyLevel.VERY_HARD)
        assert new_diff == DifficultyLevel.VERY_HARD

    def test_no_retreat_below_min(self):
        """Test that can't retreat below min difficulty."""
        strategy = LinearStrategy(wrong_to_retreat=1)
        metrics = PerformanceMetrics()

        metrics.record_result(DifficultyLevel.VERY_EASY, 0.0, False)

        new_diff = strategy.select_difficulty(metrics, DifficultyLevel.VERY_EASY)
        assert new_diff == DifficultyLevel.VERY_EASY


class TestPerformanceBasedStrategy:
    """Tests for PerformanceBasedStrategy."""

    def test_advance_when_accuracy_high(self):
        """Test advancement when accuracy is above target."""
        strategy = PerformanceBasedStrategy(
            target_accuracy=0.75,
            tolerance=0.1,
            min_problems=3,
        )
        metrics = PerformanceMetrics()

        # Get perfect accuracy (above 0.85)
        for _ in range(5):
            metrics.record_result(DifficultyLevel.MEDIUM, 1.0, True)

        assert strategy.should_advance(metrics, DifficultyLevel.MEDIUM)

    def test_retreat_when_accuracy_low(self):
        """Test retreat when accuracy is below target."""
        strategy = PerformanceBasedStrategy(
            target_accuracy=0.75,
            tolerance=0.1,
            min_problems=3,
        )
        metrics = PerformanceMetrics()

        # Get low accuracy (below 0.65)
        for _ in range(5):
            metrics.record_result(DifficultyLevel.MEDIUM, 0.0, False)

        assert strategy.should_retreat(metrics, DifficultyLevel.MEDIUM)

    def test_stay_when_in_target_range(self):
        """Test staying when accuracy is in target range."""
        strategy = PerformanceBasedStrategy(
            target_accuracy=0.75,
            tolerance=0.1,
            min_problems=3,
        )
        metrics = PerformanceMetrics()

        # Get ~75% accuracy
        for _ in range(3):
            metrics.record_result(DifficultyLevel.MEDIUM, 1.0, True)
        metrics.record_result(DifficultyLevel.MEDIUM, 0.0, False)

        assert not strategy.should_advance(metrics, DifficultyLevel.MEDIUM)
        assert not strategy.should_retreat(metrics, DifficultyLevel.MEDIUM)

    def test_wait_for_min_problems(self):
        """Test waiting for minimum problems before adjusting."""
        strategy = PerformanceBasedStrategy(min_problems=5)
        metrics = PerformanceMetrics()

        # Only 3 problems
        for _ in range(3):
            metrics.record_result(DifficultyLevel.MEDIUM, 1.0, True)

        # Should not advance yet (need 5 problems)
        assert not strategy.should_advance(metrics, DifficultyLevel.MEDIUM)


class TestSelfPacedStrategy:
    """Tests for SelfPacedStrategy."""

    def test_ema_update(self):
        """Test EMA updating."""
        strategy = SelfPacedStrategy(alpha=0.5)

        strategy.update_ema(DifficultyLevel.MEDIUM, 1.0)
        # EMA = 0.5 * 1.0 + 0.5 * 0.5 = 0.75

        strategy.update_ema(DifficultyLevel.MEDIUM, 1.0)
        # EMA = 0.5 * 1.0 + 0.5 * 0.75 = 0.875

        assert strategy._ema_scores[DifficultyLevel.MEDIUM] == pytest.approx(0.875)

    def test_advance_on_high_ema(self):
        """Test advancement when EMA is high."""
        strategy = SelfPacedStrategy(
            alpha=1.0,  # Immediate response
            advance_threshold=0.8,
        )
        metrics = PerformanceMetrics()

        strategy.update_ema(DifficultyLevel.MEDIUM, 0.9)

        assert strategy.should_advance(metrics, DifficultyLevel.MEDIUM)

    def test_retreat_on_low_ema(self):
        """Test retreat when EMA is low."""
        strategy = SelfPacedStrategy(
            alpha=1.0,
            retreat_threshold=0.5,
        )
        metrics = PerformanceMetrics()

        strategy.update_ema(DifficultyLevel.MEDIUM, 0.3)

        assert strategy.should_retreat(metrics, DifficultyLevel.MEDIUM)


class TestProgressTracker:
    """Tests for ProgressTracker."""

    def test_record_result(self):
        """Test recording a result."""
        tracker = ProgressTracker()
        problem = MagicMock()
        problem.id = "test-1"
        problem.domain = DomainType.ARITHMETIC
        problem.difficulty = DifficultyLevel.MEDIUM

        result = VerificationResult(correct=True, score=1.0)

        tracker.record_result(problem, result)

        assert tracker.session_problems == 1
        assert tracker.session_correct == 1
        assert tracker.session_accuracy == 1.0

    def test_get_metrics(self):
        """Test getting domain metrics."""
        tracker = ProgressTracker()

        metrics = tracker.get_metrics(DomainType.ARITHMETIC)

        assert metrics is not None
        assert metrics.total_problems == 0

    def test_current_difficulty(self):
        """Test current difficulty tracking."""
        tracker = ProgressTracker()

        # Default is MEDIUM
        diff = tracker.get_current_difficulty(DomainType.ARITHMETIC)
        assert diff == DifficultyLevel.MEDIUM

        # Set a new difficulty
        tracker.set_difficulty(DomainType.ARITHMETIC, DifficultyLevel.HARD)
        diff = tracker.get_current_difficulty(DomainType.ARITHMETIC)
        assert diff == DifficultyLevel.HARD

    def test_weakest_domain(self):
        """Test finding weakest domain."""
        tracker = ProgressTracker()

        # Add results for two domains
        problem_arith = MagicMock()
        problem_arith.id = "a1"
        problem_arith.domain = DomainType.ARITHMETIC
        problem_arith.difficulty = DifficultyLevel.MEDIUM

        problem_frac = MagicMock()
        problem_frac.id = "f1"
        problem_frac.domain = DomainType.FRACTIONS
        problem_frac.difficulty = DifficultyLevel.MEDIUM

        # Arithmetic: 100% (2/2)
        tracker.record_result(problem_arith, VerificationResult(correct=True, score=1.0))
        tracker.record_result(problem_arith, VerificationResult(correct=True, score=1.0))

        # Fractions: 50% (1/2)
        tracker.record_result(problem_frac, VerificationResult(correct=True, score=1.0))
        tracker.record_result(problem_frac, VerificationResult(correct=False, score=0.0))

        # Fractions should be weakest
        assert tracker.get_weakest_domain() == DomainType.FRACTIONS

    def test_strongest_domain(self):
        """Test finding strongest domain."""
        tracker = ProgressTracker()

        problem_arith = MagicMock()
        problem_arith.id = "a1"
        problem_arith.domain = DomainType.ARITHMETIC
        problem_arith.difficulty = DifficultyLevel.MEDIUM

        problem_frac = MagicMock()
        problem_frac.id = "f1"
        problem_frac.domain = DomainType.FRACTIONS
        problem_frac.difficulty = DifficultyLevel.MEDIUM

        # Arithmetic: 100%
        tracker.record_result(problem_arith, VerificationResult(correct=True, score=1.0))

        # Fractions: 50%
        tracker.record_result(problem_frac, VerificationResult(correct=True, score=1.0))
        tracker.record_result(problem_frac, VerificationResult(correct=False, score=0.0))

        assert tracker.get_strongest_domain() == DomainType.ARITHMETIC

    def test_problem_history(self):
        """Test problem history tracking."""
        tracker = ProgressTracker(max_history=5)

        problem = MagicMock()
        problem.id = "test"
        problem.domain = DomainType.ARITHMETIC
        problem.difficulty = DifficultyLevel.MEDIUM

        # Add more than max history
        for i in range(10):
            problem.id = f"test-{i}"
            tracker.record_result(problem, VerificationResult(correct=True, score=1.0))

        # Should only keep last 5
        assert len(tracker.problem_history) == 5
        assert tracker.problem_history[0]["problem_id"] == "test-5"


class TestCurriculumScheduler:
    """Tests for CurriculumScheduler."""

    def test_next_problem(self):
        """Test getting next problem."""
        scheduler = CurriculumScheduler(
            initial_difficulty=DifficultyLevel.EASY,
            domains=[DomainType.ARITHMETIC],
        )

        # Set the difficulty explicitly before generating
        scheduler.tracker.set_difficulty(DomainType.ARITHMETIC, DifficultyLevel.EASY)
        problem, trace = scheduler.next_problem(domain=DomainType.ARITHMETIC)

        assert problem is not None
        assert problem.domain == DomainType.ARITHMETIC
        assert problem.difficulty == DifficultyLevel.EASY

    def test_next_problem_with_domain(self):
        """Test getting next problem for specific domain."""
        scheduler = CurriculumScheduler(
            domains=[DomainType.ARITHMETIC, DomainType.FRACTIONS],
        )

        problem, trace = scheduler.next_problem(domain=DomainType.FRACTIONS)

        assert problem.domain == DomainType.FRACTIONS

    def test_record_result_updates_difficulty(self):
        """Test that recording results updates difficulty."""
        strategy = LinearStrategy(correct_to_advance=2)
        scheduler = CurriculumScheduler(
            strategy=strategy,
            initial_difficulty=DifficultyLevel.EASY,
            domains=[DomainType.ARITHMETIC],
        )

        # Set initial difficulty
        scheduler.tracker.set_difficulty(DomainType.ARITHMETIC, DifficultyLevel.EASY)

        # Get a problem
        problem, _ = scheduler.next_problem(domain=DomainType.ARITHMETIC)

        # Record two correct answers (score >= 0.9 triggers advance)
        result = VerificationResult(correct=True, score=1.0)
        scheduler.record_result(problem, result)
        scheduler.record_result(problem, result)

        # Should have advanced (EASY -> PRETTY_EASY)
        current_diff = scheduler.tracker.get_current_difficulty(DomainType.ARITHMETIC)
        assert current_diff == DifficultyLevel.PRETTY_EASY

    def test_get_summary(self):
        """Test getting curriculum summary."""
        scheduler = CurriculumScheduler(
            domains=[DomainType.ARITHMETIC],
        )

        summary = scheduler.get_summary()

        assert "session" in summary
        assert "domains" in summary
        assert "arithmetic" in summary["domains"]


class TestAdaptiveCurriculumScheduler:
    """Tests for AdaptiveCurriculumScheduler."""

    def test_spaced_repetition(self):
        """Test spaced repetition of difficult problems."""
        scheduler = AdaptiveCurriculumScheduler(
            initial_difficulty=DifficultyLevel.EASY,
            domains=[DomainType.ARITHMETIC],
            repetition_factor=1.0,  # Always repeat
        )

        # Get a problem and mark it wrong
        problem, _ = scheduler.next_problem()
        result = VerificationResult(correct=False, score=0.0)
        scheduler.record_result(problem, result)

        # Should have added to difficult problems
        assert len(scheduler._difficult_problems) == 1

    def test_mastery_tracking(self):
        """Test mastery tracking."""
        # Use a strategy that doesn't advance easily (needs many more problems)
        from chuk_math_gym.curriculum.strategies import PerformanceBasedStrategy
        strategy = PerformanceBasedStrategy(
            target_accuracy=0.75,
            min_problems=100,  # Won't advance with just 10 problems
        )
        scheduler = AdaptiveCurriculumScheduler(
            strategy=strategy,
            initial_difficulty=DifficultyLevel.EASY,
            domains=[DomainType.ARITHMETIC],
            mastery_threshold=0.8,
        )

        # Set initial difficulty
        scheduler.tracker.set_difficulty(DomainType.ARITHMETIC, DifficultyLevel.EASY)

        # Initially not mastered (no problems yet)
        assert not scheduler.is_mastered(DomainType.ARITHMETIC)

        # Get problems and record perfect results
        for i in range(10):
            problem, _ = scheduler.next_problem(domain=DomainType.ARITHMETIC)
            result = VerificationResult(correct=True, score=1.0)
            scheduler.record_result(problem, result)

        # Should be mastered now (accuracy >= 0.8 at EASY level)
        # Difficulty shouldn't have changed since min_problems=100
        assert scheduler.tracker.get_current_difficulty(DomainType.ARITHMETIC) == DifficultyLevel.EASY
        assert scheduler.is_mastered(DomainType.ARITHMETIC)

    def test_get_mastery_status(self):
        """Test getting mastery status for all domains."""
        scheduler = AdaptiveCurriculumScheduler(
            domains=[DomainType.ARITHMETIC, DomainType.FRACTIONS],
        )

        status = scheduler.get_mastery_status()

        assert "arithmetic" in status
        assert "fractions" in status


class TestCurriculumIntegration:
    """Integration tests for curriculum system."""

    def test_full_session(self):
        """Test a full training session."""
        scheduler = CurriculumScheduler(
            strategy=PerformanceBasedStrategy(
                target_accuracy=0.75,
                min_problems=3,
            ),
            initial_difficulty=DifficultyLevel.EASY,
            domains=[DomainType.ARITHMETIC],
        )

        # Run a session of 10 problems
        for i in range(10):
            problem, trace = scheduler.next_problem()

            # Simulate solving - alternate correct/wrong
            correct = i % 3 != 2  # 2/3 correct
            result = VerificationResult(
                correct=correct,
                score=1.0 if correct else 0.0,
            )
            scheduler.record_result(problem, result)

        summary = scheduler.get_summary()
        assert summary["session"]["problems"] == 10

    def test_domain_selection_focuses_on_weak(self):
        """Test that domain selection focuses on weak domains."""
        scheduler = CurriculumScheduler(
            domains=[DomainType.ARITHMETIC, DomainType.FRACTIONS],
        )

        # Make arithmetic strong
        problem_arith = MagicMock()
        problem_arith.id = "a1"
        problem_arith.domain = DomainType.ARITHMETIC
        problem_arith.difficulty = DifficultyLevel.MEDIUM
        for _ in range(5):
            scheduler.tracker.record_result(
                problem_arith,
                VerificationResult(correct=True, score=1.0)
            )

        # Make fractions weak
        problem_frac = MagicMock()
        problem_frac.id = "f1"
        problem_frac.domain = DomainType.FRACTIONS
        problem_frac.difficulty = DifficultyLevel.MEDIUM
        for _ in range(5):
            scheduler.tracker.record_result(
                problem_frac,
                VerificationResult(correct=False, score=0.0)
            )

        # Sample many problems - should favor fractions (70% chance)
        fraction_count = 0
        for _ in range(100):
            domain = scheduler._select_domain()
            if domain == DomainType.FRACTIONS:
                fraction_count += 1

        # Should be around 70%, give or take
        assert fraction_count > 50  # At least majority should be fractions
