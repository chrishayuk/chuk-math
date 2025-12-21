#!/usr/bin/env python3
"""
Comprehensive demonstration of chuk-math-gym functionality.

This script demonstrates:
1. Problem generation across all domains
2. Trace generation with step-by-step solutions
3. Verification with partial credit and error classification
4. Gym environment with rewards
5. Curriculum scheduling with adaptive difficulty
"""

import sys
sys.path.insert(0, 'src')

from chuk_math_gym.schemas.problem import DifficultyLevel, DomainType, ToolPolicy
from chuk_math_gym.schemas.verification import VerificationResult


def print_header(title: str):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_subheader(title: str):
    """Print a formatted subheader."""
    print(f"\n--- {title} ---")


# =============================================================================
# PART 1: ARITHMETIC DOMAIN
# =============================================================================

def demo_arithmetic():
    """Demonstrate arithmetic domain functionality."""
    print_header("ARITHMETIC DOMAIN")

    from chuk_math_gym.domains.arithmetic import ArithmeticGenerator, ArithmeticGymEnv
    from chuk_math_gym.verifiers.arithmetic import ArithmeticVerifier

    # --- Generation ---
    print_subheader("Problem Generation")
    generator = ArithmeticGenerator()

    problem, trace = generator.generate(
        seed=42,
        difficulty=DifficultyLevel.MEDIUM,
    )

    print(f"Problem ID: {problem.id}")
    print(f"Domain: {problem.domain.value}")
    print(f"Difficulty: {problem.difficulty.value}")
    print(f"Expression: {problem.expression}")
    print(f"Prompt: {problem.prompt}")
    print(f"Gold Answer: {problem.gold_answer}")

    # --- Trace (Step-by-Step Solution) ---
    print_subheader("Solution Trace")
    print(f"Total Steps: {trace.total_steps}")
    print(f"Total Cost: {trace.total_cost:.2f}")
    print(f"Final Value: {trace.final_value}")
    print("\nSteps:")
    for step in trace.steps:
        print(f"  Step {step.index}: {step.operation.value}")
        print(f"    {step.before_state} -> {step.after_state}")
        print(f"    Output: <{step.output}> = {step.output_value}")

    # --- Verification ---
    print_subheader("Verification")
    verifier = ArithmeticVerifier()

    # Correct answer
    result = verifier.verify_final(problem, problem.gold_answer)
    print(f"Correct answer '{problem.gold_answer}':")
    print(f"  Correct: {result.correct}, Score: {result.score}")

    # Wrong answer
    result = verifier.verify_final(problem, "999")
    print(f"Wrong answer '999':")
    print(f"  Correct: {result.correct}, Score: {result.score}")
    print(f"  Error Type: {result.error_type.value if result.error_type else 'none'}")

    # Sign error
    wrong_sign = str(-float(problem.gold_answer))
    result = verifier.verify_final(problem, wrong_sign)
    print(f"Sign error '{wrong_sign}':")
    print(f"  Correct: {result.correct}, Error Type: {result.error_type.value if result.error_type else 'none'}")

    # --- Gym Environment ---
    print_subheader("Gym Environment")
    env = ArithmeticGymEnv(
        max_steps=5,
        correct_reward=1.0,
        wrong_answer_penalty=-1.0,
        step_penalty=-0.01,
    )

    problem = env.reset(seed=123, difficulty=DifficultyLevel.EASY)
    print(f"Problem: {problem.prompt}")
    print(f"Gold: {problem.gold_answer}")

    # Submit correct answer
    obs, reward, done, info = env.step(f"ANSWER {problem.gold_answer}")
    print(f"\nSubmit correct answer:")
    print(f"  Observation: {obs}")
    print(f"  Reward: {reward:.2f}")
    print(f"  Done: {done}")

    # Reset and try wrong answer
    problem = env.reset(seed=456, difficulty=DifficultyLevel.EASY)
    print(f"\nNew Problem: {problem.prompt}")
    obs, reward, done, info = env.step("ANSWER 0")
    print(f"Submit wrong answer '0':")
    print(f"  Observation: {obs}")
    print(f"  Reward: {reward:.2f}")

    return True


# =============================================================================
# PART 2: FRACTIONS DOMAIN
# =============================================================================

def demo_fractions():
    """Demonstrate fractions domain functionality."""
    print_header("FRACTIONS DOMAIN")

    from chuk_math_gym.domains.fractions import FractionsGenerator, FractionsVerifier, FractionsGymEnv

    # --- Generation ---
    print_subheader("Problem Generation")
    generator = FractionsGenerator()

    # Generate different problem types
    for seed, desc in [(42, "simplify"), (100, "add/subtract"), (200, "multiply/divide")]:
        problem, trace = generator.generate(seed=seed, difficulty=DifficultyLevel.MEDIUM)
        print(f"\n{desc.upper()}:")
        print(f"  Expression: {problem.expression}")
        print(f"  Prompt: {problem.prompt}")
        print(f"  Answer: {problem.gold_answer}")

    # --- Detailed Trace ---
    print_subheader("Solution Trace (Fraction Addition)")
    problem, trace = generator.generate(seed=150, difficulty=DifficultyLevel.EASY)
    print(f"Problem: {problem.prompt}")
    print(f"Expression: {problem.expression}")
    print(f"\nSteps:")
    for step in trace.steps:
        print(f"  Step {step.index} [{step.operation.value}]: {step.before_state} -> {step.after_state}")
    print(f"\nFinal Answer: {problem.gold_answer}")

    # --- Verification ---
    print_subheader("Verification")
    verifier = FractionsVerifier()

    # Test equivalent fractions
    from chuk_math_gym.schemas.problem import Problem
    test_problem = Problem(
        id="test", seed=0, domain=DomainType.FRACTIONS,
        difficulty=DifficultyLevel.MEDIUM,
        prompt="Simplify", expression="4/8", gold_answer="1/2"
    )

    print("Testing equivalent fractions (gold: 1/2):")
    for answer in ["1/2", "2/4", "3/6", "0.5", "4/8"]:
        result = verifier.verify_final(test_problem, answer)
        status = "CORRECT" if result.correct else f"WRONG (score={result.score})"
        print(f"  '{answer}': {status}")

    # --- Gym Environment ---
    print_subheader("Gym Environment")
    env = FractionsGymEnv(max_steps=5)

    problem = env.reset(seed=42, difficulty=DifficultyLevel.EASY)
    print(f"Problem: {problem.prompt}")
    print(f"Expression: {problem.expression}")
    print(f"Gold: {problem.gold_answer}")

    obs, reward, done, info = env.step(f"ANSWER {problem.gold_answer}")
    print(f"\nSubmit correct answer:")
    print(f"  Reward: {reward:.2f}")
    print(f"  Correct: {info['verification_result']['correct']}")

    return True


# =============================================================================
# PART 3: LINEAR EQUATIONS DOMAIN
# =============================================================================

def demo_linear_equations():
    """Demonstrate linear equations domain functionality."""
    print_header("LINEAR EQUATIONS DOMAIN")

    from chuk_math_gym.domains.linear_equations import (
        LinearEquationsGenerator, LinearEquationsVerifier, LinearEquationsGymEnv
    )

    # --- Generation across difficulties ---
    print_subheader("Problem Generation (Various Difficulties)")
    generator = LinearEquationsGenerator()

    for diff in [DifficultyLevel.VERY_EASY, DifficultyLevel.MEDIUM, DifficultyLevel.HARD]:
        problem, trace = generator.generate(seed=42, difficulty=diff)
        print(f"\n{diff.value.upper()}:")
        print(f"  Equation: {problem.expression}")
        print(f"  Solution: x = {problem.gold_answer}")

    # --- Detailed Trace ---
    print_subheader("Solution Trace (Two-Step Equation)")
    problem, trace = generator.generate(seed=42, difficulty=DifficultyLevel.MEDIUM)
    print(f"Equation: {problem.expression}")
    print(f"\nSolution Steps:")
    for step in trace.steps:
        print(f"  Step {step.index} [{step.operation.value}]:")
        print(f"    {step.before_state}")
        print(f"    -> {step.after_state}")
    print(f"\nSolution: x = {problem.gold_answer}")

    # --- Verification by Substitution ---
    print_subheader("Verification by Substitution")
    verifier = LinearEquationsVerifier()

    # Check substitution
    equation = "2x + 3 = 7"
    print(f"Equation: {equation}")
    for value in [2.0, 3.0, 1.0]:
        result = verifier.verify_by_substitution(equation, "x", value)
        status = "SATISFIES" if result.correct else "DOES NOT SATISFY"
        print(f"  x = {value}: {status}")

    # --- Gym Environment with Tools ---
    print_subheader("Gym Environment with Tool Usage")
    env = LinearEquationsGymEnv(max_steps=10, tool_policy=ToolPolicy.ALLOWED)

    problem = env.reset(seed=100, difficulty=DifficultyLevel.EASY)
    print(f"Equation: {problem.expression}")
    print(f"Goal: Solve for x")
    print(f"Gold: x = {problem.gold_answer}")

    # Use tools to solve step by step
    print("\nUsing tools:")

    # Tool call
    obs, reward, done, info = env.step('CALL add_both {"equation": "x + 5 = 10", "value": -5}')
    print(f"  add_both(-5): {obs}")
    print(f"  Reward: {reward:.3f}")

    # Submit answer
    obs, reward, done, info = env.step(f"ANSWER {problem.gold_answer}")
    print(f"\nFinal answer:")
    print(f"  Reward: {reward:.2f}")
    print(f"  Correct: {info['verification_result']['correct']}")

    return True


# =============================================================================
# PART 4: CURRICULUM SCHEDULER
# =============================================================================

def demo_curriculum():
    """Demonstrate curriculum scheduling."""
    print_header("CURRICULUM SCHEDULER")

    from chuk_math_gym.curriculum import (
        CurriculumScheduler, AdaptiveCurriculumScheduler,
        LinearStrategy, PerformanceBasedStrategy, SelfPacedStrategy,
    )
    from chuk_math_gym.schemas.verification import VerificationResult

    # --- Basic Curriculum ---
    print_subheader("Basic Curriculum Scheduler")
    scheduler = CurriculumScheduler(
        strategy=PerformanceBasedStrategy(target_accuracy=0.75, min_problems=3),
        initial_difficulty=DifficultyLevel.EASY,
        domains=[DomainType.ARITHMETIC, DomainType.FRACTIONS],
    )

    print("Simulating a learning session...")
    print("\nInitial state:")
    for domain in [DomainType.ARITHMETIC, DomainType.FRACTIONS]:
        diff = scheduler.tracker.get_current_difficulty(domain)
        print(f"  {domain.value}: {diff.value}")

    # Simulate some problems
    results = [
        (True, 1.0), (True, 1.0), (True, 1.0), (True, 1.0),  # All correct - should advance
        (False, 0.0), (True, 1.0), (True, 1.0),  # Mixed
    ]

    print("\nSimulating problems:")
    for i, (correct, score) in enumerate(results):
        problem, trace = scheduler.next_problem(domain=DomainType.ARITHMETIC)
        result = VerificationResult(correct=correct, score=score)
        scheduler.record_result(problem, result)

        status = "CORRECT" if correct else "WRONG"
        diff = scheduler.tracker.get_current_difficulty(DomainType.ARITHMETIC)
        print(f"  Problem {i+1}: {status} -> Difficulty: {diff.value}")

    # --- Session Summary ---
    print_subheader("Session Summary")
    summary = scheduler.get_summary()
    print(f"Total Problems: {summary['session']['problems']}")
    print(f"Session Accuracy: {summary['session']['accuracy']:.1%}")
    print(f"Total Score: {summary['session']['score']:.1f}")

    # --- Adaptive Scheduler with Spaced Repetition ---
    print_subheader("Adaptive Scheduler (Spaced Repetition)")
    adaptive = AdaptiveCurriculumScheduler(
        strategy=LinearStrategy(correct_to_advance=3, wrong_to_retreat=2),
        initial_difficulty=DifficultyLevel.MEDIUM,
        domains=[DomainType.ARITHMETIC],
        mastery_threshold=0.9,
        repetition_factor=0.3,  # 30% chance to repeat difficult problems
    )

    # Simulate getting some problems wrong
    print("\nSimulating difficult problems:")
    for i in range(5):
        problem, trace = adaptive.next_problem(domain=DomainType.ARITHMETIC)
        # Alternate correct/wrong
        correct = i % 2 == 0
        result = VerificationResult(correct=correct, score=1.0 if correct else 0.0)
        adaptive.record_result(problem, result)

        print(f"  Problem {i+1}: {'CORRECT' if correct else 'WRONG'}")

    print(f"\nDifficult problems tracked: {len(adaptive._difficult_problems)}")
    print(f"Mastery status: {adaptive.get_mastery_status()}")

    # --- Strategy Comparison ---
    print_subheader("Strategy Comparison")
    from chuk_math_gym.curriculum.strategies import PerformanceMetrics

    metrics = PerformanceMetrics()
    # Simulate 10 problems with 80% accuracy
    for i in range(10):
        correct = i < 8
        metrics.record_result(DifficultyLevel.MEDIUM, 1.0 if correct else 0.0, correct)

    strategies = [
        ("Linear", LinearStrategy(correct_to_advance=5)),
        ("Performance-Based", PerformanceBasedStrategy(target_accuracy=0.75)),
        ("Self-Paced", SelfPacedStrategy(advance_threshold=0.85)),
    ]

    print(f"Current accuracy: {metrics.accuracy:.1%}")
    print("\nStrategy recommendations:")
    for name, strategy in strategies:
        if hasattr(strategy, 'update_ema'):
            # Update EMA for self-paced
            for score in metrics.recent_scores:
                strategy.update_ema(DifficultyLevel.MEDIUM, score)

        should_advance = strategy.should_advance(metrics, DifficultyLevel.MEDIUM)
        should_retreat = strategy.should_retreat(metrics, DifficultyLevel.MEDIUM)

        if should_advance:
            action = "ADVANCE"
        elif should_retreat:
            action = "RETREAT"
        else:
            action = "STAY"
        print(f"  {name}: {action}")

    return True


# =============================================================================
# PART 5: FULL TRAINING LOOP SIMULATION
# =============================================================================

def demo_training_loop():
    """Demonstrate a complete training loop."""
    print_header("FULL TRAINING LOOP SIMULATION")

    from chuk_math_gym.domains.arithmetic import ArithmeticGymEnv
    from chuk_math_gym.curriculum import CurriculumScheduler, PerformanceBasedStrategy

    # Setup
    env = ArithmeticGymEnv(
        max_steps=5,
        correct_reward=1.0,
        wrong_answer_penalty=-0.5,
        step_penalty=-0.01,
        efficiency_bonus=0.1,
    )

    scheduler = CurriculumScheduler(
        strategy=PerformanceBasedStrategy(target_accuracy=0.7, min_problems=5),
        initial_difficulty=DifficultyLevel.EASY,
        domains=[DomainType.ARITHMETIC],
    )

    print("Simulating 10 training episodes...")
    print("\nEpisode | Difficulty | Expression | Correct | Reward")
    print("-" * 60)

    total_reward = 0
    correct_count = 0

    for episode in range(10):
        # Get problem from curriculum
        problem, trace = scheduler.next_problem(domain=DomainType.ARITHMETIC)

        # Reset env with same seed to get same problem
        env_problem = env.reset(seed=problem.seed, difficulty=problem.difficulty)

        # Simulate agent decision (use gold answer 70% of time)
        import random
        random.seed(episode)
        if random.random() < 0.7:
            answer = problem.gold_answer
        else:
            answer = str(float(problem.gold_answer) + random.randint(-10, 10))

        # Take action
        obs, reward, done, info = env.step(f"ANSWER {answer}")

        # Record result in curriculum
        from chuk_math_gym.schemas.verification import VerificationResult
        result = VerificationResult(
            correct=info['verification_result']['correct'],
            score=info['verification_result']['score'],
        )
        scheduler.record_result(problem, result)

        # Track stats
        total_reward += reward
        if result.correct:
            correct_count += 1

        # Print episode
        expr_short = problem.expression[:20] + "..." if len(problem.expression) > 20 else problem.expression
        status = "YES" if result.correct else "NO"
        print(f"  {episode+1:2d}    | {problem.difficulty.value:10s} | {expr_short:20s} | {status:7s} | {reward:+.2f}")

    print("-" * 60)
    print(f"\nTraining Summary:")
    print(f"  Episodes: 10")
    print(f"  Accuracy: {correct_count}/10 ({correct_count*10}%)")
    print(f"  Total Reward: {total_reward:.2f}")
    print(f"  Avg Reward: {total_reward/10:.2f}")

    summary = scheduler.get_summary()
    print(f"  Final Difficulty: {scheduler.tracker.get_current_difficulty(DomainType.ARITHMETIC).value}")

    return True


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Run all demonstrations."""
    print("\n" + "=" * 60)
    print("  CHUK-MATH-GYM: Full System Demonstration")
    print("=" * 60)

    demos = [
        ("Arithmetic Domain", demo_arithmetic),
        ("Fractions Domain", demo_fractions),
        ("Linear Equations Domain", demo_linear_equations),
        ("Curriculum Scheduler", demo_curriculum),
        ("Full Training Loop", demo_training_loop),
    ]

    results = []
    for name, demo_func in demos:
        try:
            success = demo_func()
            results.append((name, success, None))
        except Exception as e:
            results.append((name, False, str(e)))
            import traceback
            traceback.print_exc()

    # Summary
    print_header("DEMONSTRATION SUMMARY")
    all_passed = True
    for name, success, error in results:
        status = "PASSED" if success else f"FAILED: {error}"
        print(f"  {name}: {status}")
        if not success:
            all_passed = False

    if all_passed:
        print("\n  All demonstrations completed successfully!")
        print("  The chuk-math-gym system is fully functional.")
    else:
        print("\n  Some demonstrations failed. Check errors above.")

    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
