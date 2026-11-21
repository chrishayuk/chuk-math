"""
Base Gym-style environment for math training.

Provides the standard async RL interface:
- reset() -> (observation, info)
- step(action) -> (observation, reward, terminated, truncated, info)

Extends chuk-gym-core's ReasoningEnv with math-specific functionality.
"""

from abc import abstractmethod
from typing import Any

from chuk_gym_core import (
    ReasoningEnv,
    EpisodeState,
    DifficultyLevel,
    ToolPolicy,
    SolverConfig,
    Problem,
    Trace,
    VerificationResult,
)

from chuk_math_gym.verifiers.base import Verifier


class MathGymEnv(ReasoningEnv):
    """
    Abstract base class for math Gym environments.

    Extends chuk-gym-core's ReasoningEnv with math-specific
    action handling (ANSWER and CALL commands).

    Example usage:
        env = ArithmeticGymEnv()
        obs, info = await env.reset(seed=42, difficulty=DifficultyLevel.MEDIUM)

        done = False
        while not done:
            action = agent.act(obs)
            obs, reward, terminated, truncated, info = await env.step(action)
            done = terminated or truncated
            if done:
                print(f"Success: {info.get('success')}")
    """

    def __init__(
        self,
        tool_policy: ToolPolicy = ToolPolicy.ALLOWED,
        solver_config: SolverConfig | None = None,
        max_steps: int = 10,
        step_penalty: float = -0.01,
        invalid_penalty: float = -0.1,
        hint_penalty: float = -0.1,
        correct_reward: float = 1.0,
        completion_bonus: float = 1.0,
        efficiency_multiplier: float = 0.1,
    ):
        """
        Initialize the math environment.

        Args:
            tool_policy: Default tool policy for problems
            solver_config: Solver/hint configuration
            max_steps: Maximum steps before episode ends
            step_penalty: Small penalty per step (encourages efficiency)
            invalid_penalty: Penalty for invalid actions
            hint_penalty: Penalty for using hints
            correct_reward: Reward for correct answer
            completion_bonus: Bonus for completing problem
            efficiency_multiplier: Multiplier for efficiency bonus
        """
        # Create solver config from tool policy if not provided
        if solver_config is None:
            if tool_policy == ToolPolicy.FORBIDDEN:
                solver_config = SolverConfig.solver_free()
            else:
                solver_config = SolverConfig()

        super().__init__(
            solver_config=solver_config,
            max_steps=max_steps,
            step_penalty=step_penalty,
            invalid_penalty=invalid_penalty,
            hint_penalty=hint_penalty,
            correct_reward=correct_reward,
            completion_bonus=completion_bonus,
            efficiency_multiplier=efficiency_multiplier,
        )

        self.tool_policy = tool_policy
        self._verifier: Verifier | None = None

    # --- Abstract methods from ReasoningEnv ---

    @property
    @abstractmethod
    def domain(self) -> str:
        """Domain identifier (e.g., 'arithmetic')."""
        pass

    @abstractmethod
    async def _generate_problem(
        self,
        seed: int,
        difficulty: DifficultyLevel,
    ) -> Problem:
        """Generate a problem for this domain."""
        pass

    @abstractmethod
    async def _generate_trace(self, problem: Problem) -> Trace | None:
        """Generate the canonical solution trace for a problem."""
        pass

    @abstractmethod
    def _get_verifier(self) -> Verifier:
        """Get the verifier for this domain."""
        pass

    # --- Implement core ReasoningEnv methods ---

    async def _validate_action(self, action: str) -> tuple[bool, float, str]:
        """
        Validate and execute a math action.

        Supports:
        - "ANSWER <value>": Submit a final answer
        - "CALL <tool_name> <json_args>": Make a tool call
        - Direct value: Interpreted as ANSWER

        Returns:
            Tuple of (success, reward, message)
        """
        assert self.state is not None

        action = action.strip()

        if action.upper().startswith("ANSWER"):
            return await self._handle_answer(action)
        elif action.upper().startswith("CALL"):
            return await self._handle_tool_call(action)
        else:
            # Try to interpret as direct answer
            return await self._handle_answer(f"ANSWER {action}")

    def _is_complete(self) -> bool:
        """Check if the episode is complete (answer submitted)."""
        if self.state is None or self.state.final_result is None:
            return False
        # In math problems, once an answer is submitted the episode ends
        # regardless of correctness (unlike puzzles where you keep trying)
        return True

    def _get_observation(self) -> dict[str, Any]:
        """Get the current observation."""
        if self.state is None:
            return {"error": "no_state"}

        obs: dict[str, Any] = {
            "prompt": self.state.problem.prompt,
            "domain": self.state.problem.domain,
            "difficulty": self.state.problem.difficulty.value,
            "tool_policy": self.state.problem.tool_policy.value,
            "steps_taken": self.state.steps_taken,
            "hints_used": self.state.hints_used,
        }

        if self.state.problem.expression:
            obs["expression"] = self.state.problem.expression

        if self.state.done and self.state.final_result is not None:
            obs["done"] = True
            obs["correct"] = self.state.final_result.correct
            obs["score"] = self.state.final_result.score

        return obs

    # --- Math-specific action handlers ---

    async def _handle_answer(self, action: str) -> tuple[bool, float, str]:
        """Handle an answer submission."""
        assert self.state is not None

        # Extract answer value
        parts = action.split(maxsplit=1)
        if len(parts) < 2:
            return (False, 0.0, "Invalid answer format. Use: ANSWER <value>")

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

        # Store result
        self.state.final_result = result
        self.state.done = True

        if result.correct:
            return (True, 0.0, f"Correct! Score: {result.score}")
        else:
            return (False, 0.0, result.error_message or "Incorrect answer.")

    async def _handle_tool_call(self, action: str) -> tuple[bool, float, str]:
        """Handle a tool call."""
        assert self.state is not None

        # Check tool policy
        if self.state.problem.tool_policy == ToolPolicy.FORBIDDEN:
            return (False, -0.1, "Tool calls are forbidden for this problem.")

        # Parse tool call: CALL <tool_name> <json_args>
        parts = action.split(maxsplit=2)
        if len(parts) < 2:
            return (False, 0.0, "Invalid tool call format. Use: CALL <tool_name> <args>")

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
        self.state.tool_calls.append(
            {
                "name": tool_name,
                "args": args,
            }
        )

        # Execute tool
        result = await self._execute_tool(tool_name, args)

        return (True, 0.0, f"Tool result: {result}")

    async def _execute_tool(self, tool_name: str, args: dict[str, Any]) -> str:
        """
        Execute a tool call. Override in subclasses for real tool integration.

        Default implementation returns a placeholder.
        """
        return f"[Tool '{tool_name}' executed with args: {args}]"

    # --- Convenience methods ---

    def get_allowed_actions(self) -> list[str]:
        """Return list of allowed action types for current problem."""
        actions = ["ANSWER <value>"]

        if self.state and self.state.problem.tool_policy != ToolPolicy.FORBIDDEN:
            actions.append("CALL <tool_name> <args>")

        return actions

    def render(self, mode: str = "ansi") -> str | None:
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

        if self.state.done and self.state.final_result is not None:
            lines.append(f"Episode done. Correct: {self.state.final_result.correct}")

        return "\n".join(lines)

    @property
    def current_trace(self) -> Trace | None:
        """Get the current trace (if any)."""
        return self.state.trace if self.state else None
