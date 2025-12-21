# chuk-math-gym

A verifiable reasoning and tool-use training environment for mathematical problem-solving.

## Overview

chuk-math-gym provides a Gymnasium-style environment for training LLM agents on mathematical reasoning with verifiable rewards. It generates problems with deterministic seeding, produces machine-checkable solution traces, and provides local verification with partial credit.

### Key Features

- **Problem Generation**: Deterministic seeding for reproducible problem sets
- **Solution Traces**: Step-by-step traces with machine-checkable verification
- **Partial Credit**: Granular scoring based on correct intermediate steps
- **Gym-style Interface**: Standard `reset()`/`step()` RL environment API
- **Multiple Domains**: Arithmetic, fractions, and linear equations
- **Curriculum Learning**: Adaptive difficulty scheduling strategies

## Installation

### Using uv (recommended)

```bash
pip install uv
uv sync --reinstall
```

### Using pip

```bash
pip install -r requirements.txt
```

## Quick Start

### Using the Gym Environment

```python
from chuk_math_gym import MathGymEnv, DomainType, DifficultyLevel

# Create environment for arithmetic problems
env = MathGymEnv(
    domain=DomainType.ARITHMETIC,
    difficulty=DifficultyLevel.EASY
)

# Reset to get a new problem
problem = env.reset(seed=42)
print(f"Problem: {problem.prompt}")
print(f"Expression: {problem.expression}")

# Submit an answer
result = env.step("42")
print(f"Correct: {result.correct}")
print(f"Score: {result.score}")
```

### Domain-Specific Environments

```python
from chuk_math_gym.domains.arithmetic import ArithmeticEnv
from chuk_math_gym.domains.fractions import FractionsEnv
from chuk_math_gym.domains.linear_equations import LinearEquationsEnv

# Arithmetic environment
arith_env = ArithmeticEnv(difficulty=DifficultyLevel.MEDIUM)
problem = arith_env.reset(seed=123)

# Fractions environment
frac_env = FractionsEnv(difficulty=DifficultyLevel.EASY)
problem = frac_env.reset(seed=456)

# Linear equations environment
eq_env = LinearEquationsEnv(difficulty=DifficultyLevel.HARD)
problem = eq_env.reset(seed=789)
```

### Verifying Solutions

```python
from chuk_math_gym.verifiers.arithmetic import ArithmeticVerifier
from chuk_math_gym.schemas.problem import Problem, DomainType, DifficultyLevel

verifier = ArithmeticVerifier()

# Verify a final answer
result = verifier.verify_answer(
    problem=problem,
    answer="42",
    gold_answer="42"
)
print(f"Correct: {result.correct}, Score: {result.score}")

# Verify a complete trace with partial credit
trace_result = verifier.verify_trace(problem, trace)
print(f"Partial credit: {trace_result.score}")
```

### Curriculum Learning

```python
from chuk_math_gym.curriculum import CurriculumScheduler
from chuk_math_gym.curriculum.strategies import (
    LinearProgressionStrategy,
    AdaptiveStrategy,
    MasteryBasedStrategy
)

# Create scheduler with adaptive difficulty
scheduler = CurriculumScheduler(
    strategy=AdaptiveStrategy(
        success_threshold=0.8,
        failure_threshold=0.4
    )
)

# Get current difficulty
difficulty = scheduler.get_difficulty()

# Update based on performance
scheduler.update(score=0.9, correct=True)
```

## Project Structure

```
src/chuk_math_gym/
├── domains/           # Domain-specific implementations
│   ├── arithmetic/    # Arithmetic expression problems
│   ├── fractions/     # Fraction manipulation problems
│   └── linear_equations/  # Equation solving problems
├── env/               # Gymnasium environment base
├── schemas/           # Pydantic models for problems, traces, verification
├── verifiers/         # Answer and trace verification
├── trace/             # Solution trace generation
├── curriculum/        # Difficulty scheduling strategies
├── generators/        # Problem generation base classes
├── explanations/      # Step-by-step explanation generation
├── expression_generator/  # Random expression generation
└── compiler/          # Expression parsing and compilation
```

## Difficulty Levels

Problems can be generated at seven difficulty levels:

| Level | Description |
|-------|-------------|
| `VERY_EASY` | Simple single-operation problems |
| `EASY` | Basic problems with small numbers |
| `PRETTY_EASY` | Slightly more complex expressions |
| `MEDIUM` | Multi-step problems |
| `HARD` | Complex expressions with decimals |
| `PRETTY_HARD` | Challenging multi-operation problems |
| `VERY_HARD` | Advanced problems with large numbers |

## Testing

Run the test suite:

```bash
# Using pytest directly
uv run pytest

# With coverage
uv run pytest --cov=src/chuk_math_gym --cov-report=term-missing

# Run all checks (lint + format + tests)
make check
```

Current test coverage: **96%** with **632 tests**.

## CLI Tools

### Expression Generator

Generate random expressions at specified difficulty:

```bash
python expression_generator_cli.py --difficulty "medium"
```

### Compiler

Compile expressions with step-by-step explanations:

```bash
uv run main.py "3 + 5 * (10 - 4)" --format jsonl
```

With LLM-enhanced explanations:

```bash
uv run main.py "3 + 5 * (10 - 4)" --llm "phi4" --format jsonl
```

### Generate Training Samples

```bash
# Chat-style samples
python generate_chat_samples.py -n 5 -d "easy" --llm "granite3.1-dense"

# Verifier training samples
python generate_verifier_samples.py -n 20 -d "medium"
```

## Schemas

### Problem

```python
from chuk_math_gym import Problem, DomainType, DifficultyLevel

problem = Problem(
    id="prob_001",
    seed=42,
    domain=DomainType.ARITHMETIC,
    difficulty=DifficultyLevel.EASY,
    prompt="Calculate: 3 + 5",
    expression="3 + 5",
    gold_answer="8"
)
```

### Trace

```python
from chuk_math_gym import Trace, Step, StepOperation

trace = Trace(
    problem_id="prob_001",
    steps=[
        Step(
            index=0,
            operation=StepOperation.ADD,
            before_state="3 + 5",
            after_state="8",
            output_value=8.0
        )
    ]
)
```

### Verification Result

```python
from chuk_math_gym import VerificationResult

result = VerificationResult(
    correct=True,
    score=1.0,
    error_type=None,
    feedback="Correct answer!"
)
```

## License

MIT License
