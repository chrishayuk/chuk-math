"""
Base Gym-style environment for math training.

Provides the standard RL interface:
- reset() -> observation
- step(action) -> (observation, reward, done, info)

Designed to integrate with:
- Standard RL frameworks (stable-baselines3, etc.)
- puzzle-arcade-server
- Custom training loops
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional, Tuple
import random

from chuk_math_gym.schemas.problem import (
    Problem,
    DomainType,
    DifficultyLevel,
    ToolPolicy,
)
from chuk_math_gym.schemas.trace import Trace
from chuk_math_gym.schemas.verification import VerificationResult
from chuk_math_gym.verifiers.base import Verifier


@dataclass
class EpisodeState:
    """State of a single episode."""

    problem: Problem
    trace: Optional[Trace] = None
    tool_calls: list[dict] = field(default_factory=list)
    steps_taken: int = 0
    done: bool = False
    final_result: Optional[VerificationResult] = None


class MathGymEnv(ABC):
    """
    Abstract base class for math Gym environments.

    Subclasses implement domain-specific problem generation
    and action handling.

    Example usage:
        env = ArithmeticGymEnv()
        problem = env.reset(seed=42, difficulty=DifficultyLevel.MEDIUM)

        done = False
        while not done:
            action = agent.act(problem.prompt)
            obs, reward, done, info = env.step(action)
            if done:
                print(f"Reward: {reward}")
    """

    def __init__(
        self,
        tool_policy: ToolPolicy = ToolPolicy.ALLOWED,
        max_steps: int = 10,
        step_penalty: float = -0.01,
        wrong_answer_penalty: float = -1.0,
        correct_reward: float = 1.0,
        efficiency_bonus: float = 0.1,
    ):
        """
        Initialize the environment.

        Args:
            tool_policy: Default tool policy for problems
            max_steps: Maximum steps before episode ends
            step_penalty: Small penalty per step (encourages efficiency)
            wrong_answer_penalty: Penalty for wrong final answer
            correct_reward: Reward for correct answer
            efficiency_bonus: Bonus for solving with minimal steps
        """
        self.tool_policy = tool_policy
        self.max_steps = max_steps
        self.step_penalty = step_penalty
        self.wrong_answer_penalty = wrong_answer_penalty
        self.correct_reward = correct_reward
        self.efficiency_bonus = efficiency_bonus

        # Current episode state
        self.state: Optional[EpisodeState] = None
        self._rng = random.Random()

    @abstractmethod
    def _generate_problem(
        self,
        seed: int,
        difficulty: DifficultyLevel,
    ) -> Problem:
        """Generate a problem for this domain."""
        pass

    @abstractmethod
    def _generate_trace(self, problem: Problem) -> Trace:
        """Generate the canonical solution trace for a problem."""
        pass

    @abstractmethod
    def _get_verifier(self) -> Verifier:
        """Get the verifier for this domain."""
        pass

    def reset(
        self,
        seed: Optional[int] = None,
        difficulty: Optional[DifficultyLevel] = None,
        tool_policy: Optional[ToolPolicy] = None,
    ) -> Problem:
        """
        Reset the environment and return a new problem.

        Args:
            seed: Random seed for reproducibility (None = random)
            difficulty: Difficulty level (None = random)
            tool_policy: Override default tool policy

        Returns:
            The generated Problem
        """
        # Handle seed
        if seed is None:
            seed = random.randint(0, 2**31 - 1)
        self._rng.seed(seed)

        # Handle difficulty
        if difficulty is None:
            difficulty = self._rng.choice(list(DifficultyLevel))

        # Generate problem
        problem = self._generate_problem(seed, difficulty)

        # Apply tool policy override
        if tool_policy is not None:
            problem.tool_policy = tool_policy
        elif self.tool_policy != ToolPolicy.ALLOWED:
            problem.tool_policy = self.tool_policy

        # Generate trace for verification
        trace = self._generate_trace(problem)

        # Initialize episode state
        self.state = EpisodeState(
            problem=problem,
            trace=trace,
            tool_calls=[],
            steps_taken=0,
            done=False,
        )

        return problem

    def step(self, action: str) -> Tuple[str, float, bool, dict]:
        """
        Take an action in the environment.

        Actions can be:
        - "ANSWER <value>": Submit a final answer
        - "CALL <tool_name> <json_args>": Make a tool call

        Args:
            action: Action string

        Returns:
            Tuple of (observation, reward, done, info)
            - observation: Feedback string
            - reward: Reward signal
            - done: Whether episode is complete
            - info: Additional information dict
        """
        if self.state is None:
            raise RuntimeError("Must call reset() before step()")

        if self.state.done:
            raise RuntimeError("Episode is done. Call reset() to start new episode.")

        self.state.steps_taken += 1
        reward = self.step_penalty  # Base step penalty

        # Parse action
        action = action.strip()

        if action.upper().startswith("ANSWER"):
            return self._handle_answer(action)
        elif action.upper().startswith("CALL"):
            return self._handle_tool_call(action)
        else:
            # Try to interpret as direct answer
            return self._handle_answer(f"ANSWER {action}")

    def _handle_answer(self, action: str) -> Tuple[str, float, bool, dict]:
        """Handle an answer submission."""
        # Extract answer value
        parts = action.split(maxsplit=1)
        if len(parts) < 2:
            return (
                "Invalid answer format. Use: ANSWER <value>",
                self.step_penalty,
                False,
                {"error": "invalid_format"},
            )

        candidate = parts[1].strip()

        # Verify the answer
        verifier = self._get_verifier()
        result = verifier.verify_final(self.state.problem, candidate)

        # Grade tool usage
        tool_grades = verifier.grade_tool_usage(
            self.state.problem,
            self.state.tool_calls,
        )
        result.tool_grades = tool_grades
        result.tool_calls_made = len(self.state.tool_calls)
        result.tool_calls_valid = sum(1 for g in tool_grades if g.valid)

        # Check for policy violation
        if self.state.problem.tool_policy == ToolPolicy.FORBIDDEN:
            if self.state.tool_calls:
                result.tool_policy_violated = True

        # Compute reward
        reward = result.to_reward(
            correct_reward=self.correct_reward,
            wrong_penalty=self.wrong_answer_penalty,
        )

        # Efficiency bonus
        if result.correct and self.state.steps_taken <= 3:
            reward += self.efficiency_bonus

        # End episode
        self.state.done = True
        self.state.final_result = result

        observation = self._format_result(result)

        return (
            observation,
            reward,
            True,
            {
                "verification_result": result.model_dump(),
                "steps_taken": self.state.steps_taken,
                "tool_calls": len(self.state.tool_calls),
            },
        )

    def _handle_tool_call(self, action: str) -> Tuple[str, float, bool, dict]:
        """Handle a tool call."""
        # Check tool policy
        if self.state.problem.tool_policy == ToolPolicy.FORBIDDEN:
            return (
                "Tool calls are forbidden for this problem.",
                self.step_penalty - 0.1,  # Extra penalty
                False,
                {"error": "tool_forbidden"},
            )

        # Parse tool call: CALL <tool_name> <json_args>
        parts = action.split(maxsplit=2)
        if len(parts) < 2:
            return (
                "Invalid tool call format. Use: CALL <tool_name> <args>",
                self.step_penalty,
                False,
                {"error": "invalid_format"},
            )

        tool_name = parts[1]
        args_str = parts[2] if len(parts) > 2 else "{}"

        # Parse args
        import json
        try:
            args = json.loads(args_str)
        except json.JSONDecodeError:
            # Try as simple value
            args = {"value": args_str}

        # Record the tool call
        self.state.tool_calls.append({
            "name": tool_name,
            "args": args,
        })

        # Simulate tool execution (subclasses can override)
        result = self._execute_tool(tool_name, args)

        # Check max steps
        if self.state.steps_taken >= self.max_steps:
            self.state.done = True
            return (
                f"Tool result: {result}\nMax steps reached. Episode ended.",
                self.step_penalty + self.wrong_answer_penalty,
                True,
                {"error": "max_steps", "tool_result": result},
            )

        return (
            f"Tool result: {result}",
            self.step_penalty,
            False,
            {"tool_result": result},
        )

    def _execute_tool(self, tool_name: str, args: dict) -> str:
        """
        Execute a tool call. Override in subclasses for real tool integration.

        Default implementation returns a placeholder.
        """
        return f"[Tool '{tool_name}' executed with args: {args}]"

    def _format_result(self, result: VerificationResult) -> str:
        """Format verification result as observation string."""
        if result.correct:
            return f"Correct! Score: {result.score}"
        else:
            return f"Incorrect. {result.error_message or 'Wrong answer.'}"

    def get_allowed_actions(self) -> list[str]:
        """Return list of allowed action types for current problem."""
        actions = ["ANSWER <value>"]

        if self.state and self.state.problem.tool_policy != ToolPolicy.FORBIDDEN:
            actions.append("CALL <tool_name> <args>")

        return actions

    def render(self) -> str:
        """Render current state as text."""
        if self.state is None:
            return "No active episode. Call reset() to start."

        lines = [
            f"Problem: {self.state.problem.prompt}",
            f"Difficulty: {self.state.problem.difficulty.value}",
            f"Tool policy: {self.state.problem.tool_policy.value}",
            f"Steps taken: {self.state.steps_taken}",
            f"Tool calls: {len(self.state.tool_calls)}",
        ]

        if self.state.done:
            lines.append(f"Episode done. Correct: {self.state.final_result.correct}")

        return "\n".join(lines)

    @property
    def current_problem(self) -> Optional[Problem]:
        """Get the current problem (if any)."""
        return self.state.problem if self.state else None

    @property
    def current_trace(self) -> Optional[Trace]:
        """Get the current trace (if any)."""
        return self.state.trace if self.state else None
