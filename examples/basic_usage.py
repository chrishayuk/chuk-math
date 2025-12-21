#!/usr/bin/env python3
"""
Basic usage example for chuk-math-gym.

This demonstrates the core features:
1. Problem generation with deterministic seeding
2. Local verification with error classification
3. Gym-style environment for RL training
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from chuk_math_gym import (
    Problem,
    DomainType,
    DifficultyLevel,
    ToolPolicy,
    VerificationResult,
    ErrorType,
)
from chuk_math_gym.domains.arithmetic import ArithmeticGenerator, ArithmeticGymEnv
from chuk_math_gym.verifiers.arithmetic import ArithmeticVerifier


def example_problem_generation():
    """Generate problems with the new schema."""
    print("=" * 60)
    print("Example 1: Problem Generation")
    print("=" * 60)

    generator = ArithmeticGenerator()

    # Generate a problem with a specific seed (reproducible)
    problem, trace = generator.generate(
        seed=42,
        difficulty=DifficultyLevel.MEDIUM,
    )

    print(f"\nProblem ID: {problem.id}")
    print(f"Seed: {problem.seed}")
    print(f"Difficulty: {problem.difficulty.value}")
    print(f"Prompt: {problem.prompt}")
    print(f"Expression: {problem.expression}")
    print(f"Gold Answer: {problem.gold_answer}")
    print(f"Operations: {problem.operation_count}")
    print(f"Tags: {problem.tags}")

    print(f"\nTrace has {trace.total_steps} steps:")
    for step in trace.steps[:5]:  # Show first 5 steps
        print(f"  Step {step.index}: {step.operation.value} -> {step.output}={step.output_value}")

    return problem, trace


def example_verification():
    """Verify answers with error classification."""
    print("\n" + "=" * 60)
    print("Example 2: Answer Verification")
    print("=" * 60)

    verifier = ArithmeticVerifier()

    # Create a simple problem
    problem = Problem(
        id="demo_1",
        seed=1,
        domain=DomainType.ARITHMETIC,
        difficulty=DifficultyLevel.EASY,
        prompt="What is 7 * 8?",
        expression="7 * 8",
        gold_answer="56",
    )

    print(f"\nProblem: {problem.prompt}")
    print(f"Gold answer: {problem.gold_answer}")

    # Test various answers
    test_answers = ["56", "65", "-56", "57", "not a number"]

    for answer in test_answers:
        result = verifier.verify_final(problem, answer)
        status = "CORRECT" if result.correct else "WRONG"
        print(f"\n  Answer '{answer}': {status}")
        print(f"    Score: {result.score}")
        print(f"    Error type: {result.error_type.value}")
        if result.error_message:
            print(f"    Message: {result.error_message}")


def example_gym_environment():
    """Use the Gym-style environment."""
    print("\n" + "=" * 60)
    print("Example 3: Gym Environment")
    print("=" * 60)

    # Create environment with tool support
    env = ArithmeticGymEnv(
        tool_policy=ToolPolicy.ALLOWED,
        max_steps=5,
    )

    # Reset to get a new problem
    problem = env.reset(seed=123, difficulty=DifficultyLevel.EASY)

    print(f"\nProblem: {problem.prompt}")
    print(f"Expression: {problem.expression}")
    print(f"Gold answer: {problem.gold_answer}")

    # Show environment state
    print(f"\nEnvironment state:")
    print(env.render())

    # Simulate agent making a tool call
    print("\n--- Agent uses calculator ---")
    obs, reward, done, info = env.step(f'CALL calculate {{"expression": "{problem.expression}"}}')
    print(f"Observation: {obs}")
    print(f"Reward: {reward:.3f}")
    print(f"Done: {done}")

    # Agent submits answer
    print("\n--- Agent submits answer ---")
    obs, reward, done, info = env.step(f"ANSWER {problem.gold_answer}")
    print(f"Observation: {obs}")
    print(f"Reward: {reward:.3f}")
    print(f"Done: {done}")
    print(f"Correct: {info['verification_result']['correct']}")


def example_mental_math():
    """Test mental math mode (no tools)."""
    print("\n" + "=" * 60)
    print("Example 4: Mental Math Mode")
    print("=" * 60)

    # Create environment without tools
    env = ArithmeticGymEnv(tool_policy=ToolPolicy.FORBIDDEN)

    problem = env.reset(seed=456, difficulty=DifficultyLevel.VERY_EASY)

    print(f"\nProblem: {problem.prompt}")
    print(f"Tool policy: {problem.tool_policy.value}")

    # Try to use a tool (should be blocked)
    print("\n--- Agent tries to use calculator (forbidden) ---")
    obs, reward, done, info = env.step('CALL calculate {"expression": "2 + 2"}')
    print(f"Observation: {obs}")
    print(f"Error: {info.get('error', 'none')}")

    # Submit direct answer
    print("\n--- Agent submits direct answer ---")
    obs, reward, done, info = env.step(f"ANSWER {problem.gold_answer}")
    print(f"Correct: {info['verification_result']['correct']}")


def example_batch_generation():
    """Generate a batch of problems."""
    print("\n" + "=" * 60)
    print("Example 5: Batch Generation")
    print("=" * 60)

    generator = ArithmeticGenerator()

    # Generate 5 problems
    batch = generator.generate_batch(
        count=5,
        difficulty=DifficultyLevel.MEDIUM,
        start_seed=1000,
    )

    print(f"\nGenerated {len(batch)} problems:")
    for problem, trace in batch:
        print(f"  {problem.id}: {problem.expression} = {problem.gold_answer}")


def main():
    """Run all examples."""
    example_problem_generation()
    example_verification()
    example_gym_environment()
    example_mental_math()
    example_batch_generation()

    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
