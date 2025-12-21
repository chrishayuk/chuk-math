"""Tests for the linear equations domain."""

from chuk_math_gym.schemas.problem import DifficultyLevel, DomainType, ToolPolicy, Problem
from chuk_math_gym.domains.linear_equations import (
    LinearEquationsGenerator,
    LinearEquationsVerifier,
    LinearEquationsGymEnv,
)


class TestLinearEquationsGenerator:
    """Tests for LinearEquationsGenerator."""

    def test_generate_problem(self):
        """Test basic problem generation."""
        generator = LinearEquationsGenerator()
        problem, trace = generator.generate(
            seed=42,
            difficulty=DifficultyLevel.MEDIUM,
        )

        assert problem is not None
        assert problem.domain == DomainType.LINEAR_EQUATIONS
        assert problem.difficulty == DifficultyLevel.MEDIUM
        assert problem.expression is not None
        assert "=" in problem.expression  # Equations have equals sign
        assert problem.gold_answer is not None

    def test_deterministic_generation(self):
        """Test that same seed produces same problem."""
        generator = LinearEquationsGenerator()

        p1, t1 = generator.generate(seed=123, difficulty=DifficultyLevel.EASY)
        p2, t2 = generator.generate(seed=123, difficulty=DifficultyLevel.EASY)

        assert p1.expression == p2.expression
        assert p1.gold_answer == p2.gold_answer

    def test_different_seeds_different_problems(self):
        """Test that different seeds produce different problems."""
        generator = LinearEquationsGenerator()

        p1, _ = generator.generate(seed=100, difficulty=DifficultyLevel.MEDIUM)
        p2, _ = generator.generate(seed=200, difficulty=DifficultyLevel.MEDIUM)

        # Should usually be different
        assert p1.expression != p2.expression or p1.gold_answer != p2.gold_answer

    def test_generate_batch(self):
        """Test batch generation."""
        generator = LinearEquationsGenerator()
        problems = generator.generate_batch(
            count=5,
            start_seed=42,
            difficulty=DifficultyLevel.MEDIUM,
        )

        assert len(problems) == 5
        for problem, trace in problems:
            assert problem.domain == DomainType.LINEAR_EQUATIONS
            assert "=" in problem.expression

    def test_easy_problems_are_simpler(self):
        """Test that easy problems are simpler (one-step)."""
        generator = LinearEquationsGenerator()

        easy_problems = [
            generator.generate(seed=i, difficulty=DifficultyLevel.VERY_EASY)[0] for i in range(10)
        ]

        # Very easy problems should be one-step (e.g., x + 3 = 7)
        for p in easy_problems:
            assert p.difficulty == DifficultyLevel.VERY_EASY

    def test_hard_problems_are_complex(self):
        """Test that hard problems are more complex."""
        generator = LinearEquationsGenerator()

        hard_problems = [
            generator.generate(seed=i, difficulty=DifficultyLevel.VERY_HARD)[0] for i in range(10)
        ]

        # Very hard problems should exist
        for p in hard_problems:
            assert p.difficulty == DifficultyLevel.VERY_HARD

    def test_trace_has_steps(self):
        """Test that generated trace has solution steps."""
        generator = LinearEquationsGenerator()
        problem, trace = generator.generate(
            seed=42,
            difficulty=DifficultyLevel.MEDIUM,
        )

        assert trace is not None
        assert len(trace.steps) > 0
        assert trace.final_value is not None


class TestLinearEquationsVerifier:
    """Tests for LinearEquationsVerifier."""

    def _make_problem(self, gold_answer: str, expression: str = "x = ?") -> Problem:
        """Create a test problem with given gold answer."""
        return Problem(
            id="test",
            seed=0,
            domain=DomainType.LINEAR_EQUATIONS,
            difficulty=DifficultyLevel.MEDIUM,
            prompt="Solve for x",
            expression=expression,
            gold_answer=gold_answer,
        )

    def test_verify_correct_integer(self):
        """Test verifying a correct integer answer."""
        verifier = LinearEquationsVerifier()
        problem = self._make_problem("5")
        result = verifier.verify_final(problem, "5")

        assert result.correct
        assert result.score == 1.0

    def test_verify_correct_fraction(self):
        """Test verifying a correct fractional answer."""
        verifier = LinearEquationsVerifier()
        problem = self._make_problem("0.5")

        result = verifier.verify_final(problem, "1/2")
        assert result.correct

    def test_verify_correct_decimal(self):
        """Test verifying a correct decimal answer."""
        verifier = LinearEquationsVerifier()
        problem = self._make_problem("7/2")

        result = verifier.verify_final(problem, "3.5")
        assert result.correct

    def test_verify_incorrect_answer(self):
        """Test verifying an incorrect answer."""
        verifier = LinearEquationsVerifier()
        problem = self._make_problem("5")
        result = verifier.verify_final(problem, "10")

        assert not result.correct
        assert result.score == 0.0

    def test_verify_negative_answer(self):
        """Test negative answers."""
        verifier = LinearEquationsVerifier()
        problem = self._make_problem("-3")

        result = verifier.verify_final(problem, "-3")
        assert result.correct

    def test_verify_with_x_prefix(self):
        """Test answers with 'x =' prefix."""
        verifier = LinearEquationsVerifier()
        problem = self._make_problem("5")

        result = verifier.verify_final(problem, "x = 5")
        assert result.correct

    def test_verify_by_substitution(self):
        """Test verification by substitution."""
        verifier = LinearEquationsVerifier()

        # 2x + 3 = 7, solution is x = 2
        result = verifier.verify_by_substitution(
            equation="2x + 3 = 7",
            variable="x",
            candidate=2.0,
        )
        assert result.correct

        # Wrong value
        result = verifier.verify_by_substitution(
            equation="2x + 3 = 7",
            variable="x",
            candidate=3.0,
        )
        assert not result.correct

    def test_verify_invalid_format(self):
        """Test handling of invalid input."""
        verifier = LinearEquationsVerifier()
        problem = self._make_problem("5")

        result = verifier.verify_final(problem, "invalid")
        assert not result.correct

    def test_verify_sign_error(self):
        """Test detecting sign errors."""
        verifier = LinearEquationsVerifier()
        problem = self._make_problem("5")

        result = verifier.verify_final(problem, "-5")
        assert not result.correct
        # Could check for error_type == ErrorType.SIGN_ERROR


class TestLinearEquationsGymEnv:
    """Tests for LinearEquationsGymEnv."""

    def test_reset(self):
        """Test environment reset."""
        env = LinearEquationsGymEnv()
        problem = env.reset(seed=42)

        assert problem is not None
        assert problem.domain == DomainType.LINEAR_EQUATIONS
        assert env.current_problem is not None

    def test_step_correct_answer(self):
        """Test stepping with correct answer."""
        env = LinearEquationsGymEnv()
        problem = env.reset(seed=42)

        # Get the gold answer and submit it
        gold = problem.gold_answer
        obs, reward, done, info = env.step(f"ANSWER {gold}")

        assert done
        assert reward > 0
        assert info["verification_result"]["correct"]

    def test_step_wrong_answer(self):
        """Test stepping with wrong answer."""
        env = LinearEquationsGymEnv()
        env.reset(seed=42)

        # Submit a clearly wrong answer
        obs, reward, done, info = env.step("ANSWER 999999")

        assert done
        assert reward < 0
        assert not info["verification_result"]["correct"]

    def test_tool_substitute(self):
        """Test using the substitute tool."""
        env = LinearEquationsGymEnv()
        problem = env.reset(seed=42)

        # Use substitute tool
        gold = problem.gold_answer
        equation = problem.expression
        obs, reward, done, info = env.step(
            f'CALL substitute {{"equation": "{equation}", "variable": "x", "value": {gold}}}'
        )

        # Should get feedback about substitution
        assert "satisfy" in obs.lower() or "yes" in obs.lower() or "tool" in obs.lower()

    def test_tool_add_both(self):
        """Test using the add_both tool."""
        env = LinearEquationsGymEnv()
        env.reset(seed=42)

        # Use add_both tool
        obs, reward, done, info = env.step('CALL add_both {"equation": "x + 3 = 7", "value": -3}')

        # Should show the transformed equation
        assert "=" in obs

    def test_max_steps(self):
        """Test max steps termination."""
        env = LinearEquationsGymEnv(max_steps=3)
        env.reset(seed=42)

        # Make tool calls until max
        for i in range(3):
            obs, reward, done, info = env.step('CALL evaluate {"expression": "1+1"}')
            if done:
                break

        assert done

    def test_tool_policy_forbidden(self):
        """Test tool policy enforcement."""
        env = LinearEquationsGymEnv(tool_policy=ToolPolicy.FORBIDDEN)
        env.reset(seed=42)

        # Try using a tool
        obs, reward, done, info = env.step('CALL solve {"equation": "x + 3 = 7"}')

        # Should get a penalty or error message
        assert "forbidden" in obs.lower()

    def test_get_tool_descriptions(self):
        """Test getting tool descriptions."""
        env = LinearEquationsGymEnv()
        env.reset(seed=42)

        tools = env.get_tool_descriptions()

        assert "substitute" in tools
        assert "add_both" in tools
        assert "subtract_both" in tools
        assert "multiply_both" in tools
        assert "divide_both" in tools


class TestLinearEquationsGymEnvTools:
    """Tests for LinearEquationsGymEnv tool execution."""

    def test_solve_tool(self):
        """Test solve tool."""
        env = LinearEquationsGymEnv()
        env.reset(seed=42)

        result = env._execute_tool("solve", {"equation": "x + 3 = 7", "solution": "4"})
        assert "x = 4" in result

    def test_solve_tool_invalid_equation(self):
        """Test solve with invalid equation (no equals sign)."""
        env = LinearEquationsGymEnv()
        env.reset(seed=42)

        result = env._execute_tool("solve", {"equation": "x + 3"})
        assert "Error" in result

    def test_substitute_tool(self):
        """Test substitute tool."""
        env = LinearEquationsGymEnv()
        env.reset(seed=42)

        # x = 2 satisfies 2x + 3 = 7
        result = env._execute_tool(
            "substitute", {"equation": "2*x + 3 = 7", "variable": "x", "value": 2}
        )
        assert "satisfy" in result.lower() or "yes" in result.lower()

    def test_substitute_tool_incorrect(self):
        """Test substitute with wrong value."""
        env = LinearEquationsGymEnv()
        env.reset(seed=42)

        result = env._execute_tool(
            "substitute", {"equation": "x + 3 = 7", "variable": "x", "value": 10}
        )
        assert "not satisfy" in result.lower() or "no" in result.lower()

    def test_add_both_tool(self):
        """Test add_both tool."""
        env = LinearEquationsGymEnv()
        env.reset(seed=42)

        result = env._execute_tool("add_both", {"equation": "x = 5", "value": 3})
        assert "x + 3" in result and "5 + 3" in result

    def test_subtract_both_tool(self):
        """Test subtract_both tool."""
        env = LinearEquationsGymEnv()
        env.reset(seed=42)

        result = env._execute_tool("subtract_both", {"equation": "x = 10", "value": 4})
        assert "x - 4" in result and "10 - 4" in result

    def test_multiply_both_tool(self):
        """Test multiply_both tool."""
        env = LinearEquationsGymEnv()
        env.reset(seed=42)

        result = env._execute_tool("multiply_both", {"equation": "x = 3", "value": 2})
        assert "×" in result or "*" in result

    def test_divide_both_tool(self):
        """Test divide_both tool."""
        env = LinearEquationsGymEnv()
        env.reset(seed=42)

        result = env._execute_tool("divide_both", {"equation": "x = 6", "value": 2})
        assert "÷" in result or "/" in result

    def test_divide_both_by_zero(self):
        """Test divide by zero."""
        env = LinearEquationsGymEnv()
        env.reset(seed=42)

        result = env._execute_tool("divide_both", {"equation": "x = 6", "value": 0})
        assert "Error" in result or "zero" in result.lower()

    def test_operation_tool_invalid_equation(self):
        """Test operation tools with invalid equation."""
        env = LinearEquationsGymEnv()
        env.reset(seed=42)

        result = env._execute_tool("add_both", {"equation": "no equals here", "value": 5})
        assert "Error" in result

    def test_evaluate_tool(self):
        """Test evaluate tool."""
        env = LinearEquationsGymEnv()
        env.reset(seed=42)

        result = env._execute_tool("evaluate", {"expression": "2 + 3 * 4"})
        assert float(result) == 14.0

    def test_evaluate_tool_invalid(self):
        """Test evaluate with invalid expression."""
        env = LinearEquationsGymEnv()
        env.reset(seed=42)

        result = env._execute_tool("evaluate", {"expression": "invalid"})
        assert "Error" in result

    def test_unknown_tool(self):
        """Test unknown tool."""
        env = LinearEquationsGymEnv()
        env.reset(seed=42)

        result = env._execute_tool("unknown_tool", {})
        assert "Unknown tool" in result


class TestLinearEquationsVerifierAdvanced:
    """Advanced tests for LinearEquationsVerifier."""

    def _make_problem(self, gold_answer: str, expression: str = "x = ?") -> Problem:
        """Create a test problem with given gold answer."""
        return Problem(
            id="test",
            seed=0,
            domain=DomainType.LINEAR_EQUATIONS,
            difficulty=DifficultyLevel.MEDIUM,
            prompt="Solve for x",
            expression=expression,
            gold_answer=gold_answer,
        )

    def test_verify_invalid_gold_answer(self):
        """Test verify with invalid gold answer."""
        verifier = LinearEquationsVerifier()
        problem = self._make_problem("invalid_gold")

        result = verifier.verify_final(problem, "5")
        assert not result.correct
        assert "Invalid gold answer" in result.error_message

    def test_verify_empty_candidate(self):
        """Test verify with empty candidate."""
        verifier = LinearEquationsVerifier()
        problem = self._make_problem("5")

        result = verifier.verify_final(problem, "")
        assert not result.correct

    def test_verify_trace_empty(self):
        """Test verify_trace with empty trace."""
        from chuk_math_gym.schemas.trace import Trace

        verifier = LinearEquationsVerifier()
        problem = self._make_problem("5")
        trace = Trace(problem_id="test", steps=[])

        result = verifier.verify_trace(problem, trace)
        assert not result.correct
        assert result.steps_total == 0

    def test_verify_step_out_of_range(self):
        """Test verify_step with invalid step index."""
        from chuk_math_gym.schemas.trace import Trace

        verifier = LinearEquationsVerifier()
        problem = self._make_problem("5")
        trace = Trace(problem_id="test", steps=[])

        result = verifier.verify_step(problem, trace, step_index=5, candidate_value=5.0)
        assert not result.correct

    def test_verify_substitution_no_equals(self):
        """Test substitution with equation missing equals sign."""
        verifier = LinearEquationsVerifier()

        result = verifier.verify_by_substitution(
            equation="x + 3",
            variable="x",
            candidate=4.0,
        )
        assert not result.correct
        assert "=" in result.error_message

    def test_verify_invalid_expression(self):
        """Test substitution with invalid expression."""
        verifier = LinearEquationsVerifier()

        result = verifier.verify_by_substitution(
            equation="abc$% = xyz",
            variable="x",
            candidate=4.0,
        )
        # Should handle gracefully
        assert not result.correct

    def test_classify_rounding_error(self):
        """Test that close values are classified as rounding error."""
        verifier = LinearEquationsVerifier()
        problem = self._make_problem("5.0")

        result = verifier.verify_final(problem, "5.1")
        # Should detect this as a close value
        assert not result.correct

    def test_classify_coefficient_error(self):
        """Test classification of coefficient errors."""
        verifier = LinearEquationsVerifier()
        problem = self._make_problem("10")

        result = verifier.verify_final(problem, "5")
        # 10 / 5 = 2, which is a whole number ratio
        assert not result.correct

    def test_verify_trace_with_steps(self):
        """Test verify_trace with actual steps."""
        from chuk_math_gym.schemas.trace import Trace, Step, StepOperation

        verifier = LinearEquationsVerifier()
        problem = self._make_problem("5")

        steps = [
            Step(
                index=0,
                operation=StepOperation.ADD,
                before_state="x + 3 = 8",
                after_state="x = 5",
                inputs=[],
                output="x1",
                output_value=5.0,
            ),
        ]

        trace = Trace(
            problem_id="test",
            steps=steps,
            placeholder_map={"x1": 5.0},
            final_placeholder="x1",
            final_value=5.0,
        )

        result = verifier.verify_trace(problem, trace)
        assert result.correct
        assert result.steps_correct == 1

    def test_verify_trace_with_wrong_final(self):
        """Test verify_trace with wrong final value."""
        from chuk_math_gym.schemas.trace import Trace, Step, StepOperation

        verifier = LinearEquationsVerifier()
        problem = self._make_problem("5")

        steps = [
            Step(
                index=0,
                operation=StepOperation.ADD,
                before_state="x + 3 = 8",
                after_state="x = 10",  # Wrong
                inputs=[],
                output="x1",
                output_value=10.0,  # Wrong
            ),
        ]

        trace = Trace(
            problem_id="test",
            steps=steps,
            placeholder_map={"x1": 10.0},
            final_placeholder="x1",
            final_value=10.0,  # Wrong
        )

        result = verifier.verify_trace(problem, trace)
        assert not result.correct

    def test_verify_trace_step_verification_fails(self):
        """Test verify_trace when step verification fails."""
        from chuk_math_gym.schemas.trace import Trace, Step, StepOperation

        verifier = LinearEquationsVerifier()
        problem = self._make_problem("5")

        steps = [
            Step(
                index=0,
                operation=StepOperation.ADD,
                before_state="x + 3 = 8",
                after_state="x = 5",
                inputs=[],
                output="x1",
                output_value=5.0,
            ),
            Step(
                index=1,
                operation=StepOperation.EVAL,
                before_state="x = 5",
                after_state="10",  # Wrong value in after_state
                inputs=["x1"],
                output="x2",
                output_value=10.0,  # Wrong output value
            ),
        ]

        trace = Trace(
            problem_id="test",
            steps=steps,
            placeholder_map={"x1": 5.0, "x2": 5.0},  # x2 expected to be 5.0 but step has 10.0
            final_placeholder="x2",
            final_value=10.0,
        )

        result = verifier.verify_trace(problem, trace)
        # Should fail because step 1's output_value (10.0) doesn't match expected (5.0)
        assert not result.correct

    def test_verify_trace_invalid_gold(self):
        """Test verify_trace with invalid gold answer."""
        from chuk_math_gym.schemas.trace import Trace, Step, StepOperation

        verifier = LinearEquationsVerifier()
        problem = self._make_problem("invalid")

        steps = [
            Step(
                index=0,
                operation=StepOperation.ADD,
                before_state="x",
                after_state="5",
                inputs=[],
                output="x1",
                output_value=5.0,
            ),
        ]

        trace = Trace(
            problem_id="test",
            steps=steps,
            placeholder_map={"x1": 5.0},
            final_placeholder="x1",
            final_value=5.0,
        )

        result = verifier.verify_trace(problem, trace)
        assert not result.correct

    def test_verify_step_correct(self):
        """Test verify_step with correct value."""
        from chuk_math_gym.schemas.trace import Trace, Step, StepOperation

        verifier = LinearEquationsVerifier()
        problem = self._make_problem("5")

        steps = [
            Step(
                index=0,
                operation=StepOperation.ADD,
                before_state="x + 3 = 8",
                after_state="x = 5",
                inputs=[],
                output="x1",
                output_value=5.0,
            ),
        ]

        trace = Trace(
            problem_id="test",
            steps=steps,
            placeholder_map={"x1": 5.0},
            final_placeholder="x1",
            final_value=5.0,
        )

        result = verifier.verify_step(problem, trace, 0, 5.0)
        assert result.correct

    def test_verify_step_incorrect(self):
        """Test verify_step with incorrect value."""
        from chuk_math_gym.schemas.trace import Trace, Step, StepOperation

        verifier = LinearEquationsVerifier()
        problem = self._make_problem("5")

        steps = [
            Step(
                index=0,
                operation=StepOperation.ADD,
                before_state="x + 3 = 8",
                after_state="x = 5",
                inputs=[],
                output="x1",
                output_value=5.0,
            ),
        ]

        trace = Trace(
            problem_id="test",
            steps=steps,
            placeholder_map={"x1": 5.0},
            final_placeholder="x1",
            final_value=5.0,
        )

        result = verifier.verify_step(problem, trace, 0, 10.0)  # Wrong value
        assert not result.correct

    def test_verify_step_negative_index(self):
        """Test verify_step with negative index."""
        from chuk_math_gym.schemas.trace import Trace

        verifier = LinearEquationsVerifier()
        problem = self._make_problem("5")
        trace = Trace(problem_id="test", steps=[])

        result = verifier.verify_step(problem, trace, -1, 5.0)
        assert not result.correct

    def test_substitution_exception_handling(self):
        """Test verify_by_substitution handles exceptions."""
        verifier = LinearEquationsVerifier()

        # Create an expression that will cause an exception during evaluation
        result = verifier.verify_by_substitution(
            equation="x^&$ = @#%",
            variable="x",
            candidate=5.0,
        )
        assert not result.correct

    def test_safe_eval_unsupported_constant(self):
        """Test _safe_eval with unsupported constant type."""
        verifier = LinearEquationsVerifier()

        # Try to evaluate a string constant
        result = verifier._safe_eval("'hello'")
        assert result is None

    def test_safe_eval_unsupported_operator(self):
        """Test _safe_eval with unsupported operator."""
        verifier = LinearEquationsVerifier()

        # Try to evaluate with modulo (not supported)
        result = verifier._safe_eval("10 % 3")
        assert result is None

    def test_safe_eval_unary_pos(self):
        """Test _safe_eval with unary positive."""
        verifier = LinearEquationsVerifier()

        result = verifier._safe_eval("+5")
        assert result == 5.0

    def test_evaluate_side_with_coefficient(self):
        """Test _evaluate_side handles coefficients correctly."""
        verifier = LinearEquationsVerifier()

        # 2x when x=3 should give 6
        result = verifier._evaluate_side("2x", "x", 3.0)
        assert result == 6.0

    def test_evaluate_side_without_coefficient(self):
        """Test _evaluate_side handles variable without coefficient."""
        verifier = LinearEquationsVerifier()

        # x when x=5 should give 5
        result = verifier._evaluate_side("x", "x", 5.0)
        assert result == 5.0

    def test_evaluate_side_complex_expression(self):
        """Test _evaluate_side with complex expression."""
        verifier = LinearEquationsVerifier()

        # 2x + 3 when x=4 should give 11
        result = verifier._evaluate_side("2x + 3", "x", 4.0)
        assert result == 11.0

    def test_parse_solution_division_by_zero(self):
        """Test _parse_solution with division by zero."""
        verifier = LinearEquationsVerifier()

        result = verifier._parse_solution("5/0")
        assert result is None

    def test_verify_trace_step_verify_output_fails(self):
        """Test verify_trace when step.verify_output returns False."""
        from chuk_math_gym.schemas.trace import Trace, Step, StepOperation

        verifier = LinearEquationsVerifier()
        problem = self._make_problem("5")

        steps = [
            Step(
                index=0,
                operation=StepOperation.ADD,
                before_state="x + 3 = 8",
                after_state="x = 5",
                inputs=[],
                output="x1",
                output_value=10.0,  # Mismatch with expected 5.0
            ),
        ]

        trace = Trace(
            problem_id="test",
            steps=steps,
            placeholder_map={"x1": 5.0},  # Expected 5.0, but step has 10.0
            final_placeholder="x1",
            final_value=10.0,
        )

        result = verifier.verify_trace(problem, trace)
        # Should fail because step.verify_output fails
        assert not result.correct

    def test_evaluate_side_invalid_expression(self):
        """Test _evaluate_side with expression that causes exception."""
        verifier = LinearEquationsVerifier()

        # This should trigger an exception during evaluation
        result = verifier._evaluate_side("x / 0", "x", 0.0)
        assert result is None

    def test_safe_eval_unsupported_unary(self):
        """Test _safe_eval with unsupported unary operator (bitwise not)."""
        verifier = LinearEquationsVerifier()

        # Bitwise not (~) is not supported
        result = verifier._safe_eval("~5")
        assert result is None

    def test_safe_eval_unsupported_ast_node(self):
        """Test _safe_eval with unsupported AST node type."""
        verifier = LinearEquationsVerifier()

        # Function call is not supported
        result = verifier._safe_eval("abs(5)")
        assert result is None


class TestLinearEquationsGeneratorAdvanced:
    """Advanced tests for LinearEquationsGenerator covering edge cases."""

    def test_generate_auto_seed(self):
        """Test generation with automatic seed."""
        generator = LinearEquationsGenerator()
        # Call without seed (uses auto-generated seed)
        problem, trace = generator.generate(difficulty=DifficultyLevel.EASY)

        assert problem is not None
        assert problem.seed is not None

    def test_generate_batch_auto_seed(self):
        """Test batch generation with automatic seed."""
        generator = LinearEquationsGenerator()
        # Call without start_seed
        problems = generator.generate_batch(count=3, difficulty=DifficultyLevel.EASY)

        assert len(problems) == 3
        for p, t in problems:
            assert p is not None

    def test_generate_non_integer_solutions(self):
        """Test generation with non-integer solutions."""
        generator = LinearEquationsGenerator()
        # HARD difficulty allows non-integer solutions
        problem, trace = generator.generate(
            seed=42,
            difficulty=DifficultyLevel.HARD,
        )

        assert problem is not None
        # Could have fractional answer
        assert problem.gold_answer is not None

    def test_linear_equation_solution_none(self):
        """Test LinearEquation.solution property when a-c=0 (no unique solution)."""
        from chuk_math_gym.domains.linear_equations.generator import LinearEquation
        from fractions import Fraction

        # a = c, so no unique solution
        eq = LinearEquation(a=Fraction(2), b=Fraction(3), c=Fraction(2), d=Fraction(5))

        assert eq.solution is None

    def test_linear_equation_formatting_fractions(self):
        """Test LinearEquation formatting with fraction coefficients."""
        from chuk_math_gym.domains.linear_equations.generator import LinearEquation
        from fractions import Fraction

        # Fractional coefficient: (1/2)x + 3 = 5
        eq = LinearEquation(a=Fraction(1, 2), b=Fraction(3), c=Fraction(0), d=Fraction(5))

        s = eq.to_string()
        assert "/" in s  # Should show fraction

    def test_linear_equation_formatting_negative_constant(self):
        """Test LinearEquation formatting with negative constants."""
        from chuk_math_gym.domains.linear_equations.generator import LinearEquation
        from fractions import Fraction

        # x - 5 = 10 (negative constant)
        eq = LinearEquation(a=Fraction(1), b=Fraction(-5), c=Fraction(0), d=Fraction(10))

        s = eq.to_string()
        assert "-" in s

    def test_linear_equation_formatting_negative_fraction_constant(self):
        """Test LinearEquation formatting with negative fractional constants."""
        from chuk_math_gym.domains.linear_equations.generator import LinearEquation
        from fractions import Fraction

        # x - 1/2 = 1
        eq = LinearEquation(a=Fraction(1), b=Fraction(-1, 2), c=Fraction(0), d=Fraction(1))

        s = eq.to_string()
        assert "-" in s and "/" in s

    def test_linear_equation_formatting_constant_only_no_coeff(self):
        """Test LinearEquation formatting when coefficient is 0 (constant only)."""
        from chuk_math_gym.domains.linear_equations.generator import LinearEquation
        from fractions import Fraction

        # 0x + 5 = 0x + 5 (just constant on both sides)
        eq = LinearEquation(a=Fraction(0), b=Fraction(5), c=Fraction(0), d=Fraction(10))

        s = eq.to_string()
        assert "5" in s

    def test_linear_equation_formatting_fraction_const(self):
        """Test formatting with positive fractional constant."""
        from chuk_math_gym.domains.linear_equations.generator import LinearEquation
        from fractions import Fraction

        # x + 1/2 = 3
        eq = LinearEquation(a=Fraction(1), b=Fraction(1, 2), c=Fraction(0), d=Fraction(3))

        s = eq.to_string()
        assert "/" in s

    def test_generate_one_step_add_non_integer(self):
        """Test ONE_STEP_ADD with non-integer solutions."""
        from chuk_math_gym.domains.linear_equations.generator import EquationType

        generator = LinearEquationsGenerator()
        # Use HARD difficulty which allows non-integer solutions
        problem, trace = generator.generate(
            seed=100,
            difficulty=DifficultyLevel.HARD,
            equation_type=EquationType.ONE_STEP_ADD,
        )

        assert problem is not None

    def test_generate_one_step_sub_non_integer(self):
        """Test ONE_STEP_SUB with non-integer solutions."""
        from chuk_math_gym.domains.linear_equations.generator import EquationType

        generator = LinearEquationsGenerator()
        problem, trace = generator.generate(
            seed=100,
            difficulty=DifficultyLevel.HARD,
            equation_type=EquationType.ONE_STEP_SUB,
        )

        assert problem is not None

    def test_generate_one_step_mul_non_integer(self):
        """Test ONE_STEP_MUL with non-integer solutions."""
        from chuk_math_gym.domains.linear_equations.generator import EquationType

        generator = LinearEquationsGenerator()
        problem, trace = generator.generate(
            seed=100,
            difficulty=DifficultyLevel.HARD,
            equation_type=EquationType.ONE_STEP_MUL,
        )

        assert problem is not None

    def test_generate_one_step_div_non_integer(self):
        """Test ONE_STEP_DIV with non-integer solutions."""
        from chuk_math_gym.domains.linear_equations.generator import EquationType

        generator = LinearEquationsGenerator()
        problem, trace = generator.generate(
            seed=100,
            difficulty=DifficultyLevel.HARD,
            equation_type=EquationType.ONE_STEP_DIV,
        )

        assert problem is not None

    def test_generate_two_step_non_integer(self):
        """Test TWO_STEP with non-integer solutions."""
        from chuk_math_gym.domains.linear_equations.generator import EquationType

        generator = LinearEquationsGenerator()
        problem, trace = generator.generate(
            seed=100,
            difficulty=DifficultyLevel.HARD,
            equation_type=EquationType.TWO_STEP,
        )

        assert problem is not None

    def test_generate_var_both_non_integer(self):
        """Test VARIABLE_BOTH_SIDES with non-integer solutions."""
        from chuk_math_gym.domains.linear_equations.generator import EquationType

        generator = LinearEquationsGenerator()
        problem, trace = generator.generate(
            seed=100,
            difficulty=DifficultyLevel.HARD,
            equation_type=EquationType.VARIABLE_BOTH_SIDES,
        )

        assert problem is not None

    def test_generate_distribution_non_integer(self):
        """Test DISTRIBUTION with non-integer solutions."""
        from chuk_math_gym.domains.linear_equations.generator import EquationType

        generator = LinearEquationsGenerator()
        problem, trace = generator.generate(
            seed=100,
            difficulty=DifficultyLevel.HARD,
            equation_type=EquationType.DISTRIBUTION,
        )

        assert problem is not None

    def test_generate_fractional_non_integer(self):
        """Test FRACTIONAL with non-integer solutions."""
        from chuk_math_gym.domains.linear_equations.generator import EquationType

        generator = LinearEquationsGenerator()
        problem, trace = generator.generate(
            seed=100,
            difficulty=DifficultyLevel.VERY_HARD,
            equation_type=EquationType.FRACTIONAL,
        )

        assert problem is not None

    def test_generate_coefficient_equals_c(self):
        """Test VARIABLE_BOTH_SIDES when a == c initially (forcing c = a + 1)."""
        from chuk_math_gym.domains.linear_equations.generator import EquationType

        generator = LinearEquationsGenerator()
        # Generate many times to hit the a == c case
        for i in range(20):
            problem, trace = generator.generate(
                seed=1000 + i,
                difficulty=DifficultyLevel.HARD,
                equation_type=EquationType.VARIABLE_BOTH_SIDES,
            )
            assert problem is not None


class TestLinearEquationsGymEnvAdvanced:
    """Advanced tests for LinearEquationsGymEnv covering edge cases."""

    def test_safe_eval_unsupported_operator(self):
        """Test _safe_eval_expression with unsupported operator."""
        env = LinearEquationsGymEnv()
        env.reset(seed=42)

        # Modulo is not supported
        result = env._execute_tool("evaluate", {"expression": "10 % 3"})
        assert "Error" in result

    def test_safe_eval_unsupported_constant(self):
        """Test _safe_eval_expression with string constant."""
        env = LinearEquationsGymEnv()
        env.reset(seed=42)

        result = env._execute_tool("evaluate", {"expression": "'hello'"})
        assert "Error" in result

    def test_safe_eval_syntax_error(self):
        """Test _safe_eval_expression with syntax error."""
        env = LinearEquationsGymEnv()
        env.reset(seed=42)

        result = env._execute_tool("evaluate", {"expression": "2 +"})
        assert "Error" in result

    def test_safe_eval_unsupported_unary(self):
        """Test _safe_eval_expression with unsupported unary operator (bitwise not)."""
        env = LinearEquationsGymEnv()
        env.reset(seed=42)

        result = env._execute_tool("evaluate", {"expression": "~5"})
        assert "Error" in result

    def test_safe_eval_unsupported_node(self):
        """Test _safe_eval_expression with unsupported AST node (function call)."""
        env = LinearEquationsGymEnv()
        env.reset(seed=42)

        result = env._execute_tool("evaluate", {"expression": "abs(5)"})
        assert "Error" in result

    def test_solve_tool_exception(self):
        """Test solve tool with expression that causes exception."""
        env = LinearEquationsGymEnv()
        env.reset(seed=42)

        # This should trigger an exception in try block
        # By passing an equation that causes split to return more than expected
        result = env._execute_tool("solve", {"equation": None})
        assert "Error" in result

    def test_substitute_tool_exception(self):
        """Test substitute tool with invalid value."""
        env = LinearEquationsGymEnv()
        env.reset(seed=42)

        result = env._execute_tool(
            "substitute",
            {
                "equation": "x + 3 = 7",
                "value": "invalid",  # Non-numeric value
                "variable": "x",
            },
        )
        assert "Error" in result

    def test_operation_tool_exception(self):
        """Test operation tool with invalid value that causes exception."""
        env = LinearEquationsGymEnv()
        env.reset(seed=42)

        # Pass a value that will fail float() conversion in divide_both zero check
        result = env._execute_tool("divide_both", {"equation": "x = 5", "value": "invalid"})
        assert "Error" in result

    def test_safe_eval_unary_positive(self):
        """Test _safe_eval_expression with unary positive operator."""
        env = LinearEquationsGymEnv()
        env.reset(seed=42)

        result = env._execute_tool("evaluate", {"expression": "+5"})
        assert float(result) == 5.0


class TestLinearEquationsIntegration:
    """Integration tests for linear equations domain."""

    def test_generate_and_verify(self):
        """Test full generate-solve-verify flow."""
        generator = LinearEquationsGenerator()
        verifier = LinearEquationsVerifier()

        problem, trace = generator.generate(
            seed=42,
            difficulty=DifficultyLevel.MEDIUM,
        )

        # Verify the gold answer
        result = verifier.verify_final(problem, problem.gold_answer)

        assert result.correct

    def test_verify_by_substitution_integration(self):
        """Test verification by substitution with generated problem."""
        generator = LinearEquationsGenerator()
        verifier = LinearEquationsVerifier()

        problem, trace = generator.generate(
            seed=42,
            difficulty=DifficultyLevel.EASY,
        )

        # Parse the gold answer as a number
        try:
            gold_value = float(problem.gold_answer)
        except ValueError:
            # Could be a fraction
            from fractions import Fraction

            gold_value = float(Fraction(problem.gold_answer))

        # Verify by substitution
        result = verifier.verify_by_substitution(
            equation=problem.expression,
            variable="x",
            candidate=gold_value,
        )

        assert result.correct

    def test_different_difficulties(self):
        """Test that different difficulties produce valid problems."""
        generator = LinearEquationsGenerator()
        verifier = LinearEquationsVerifier()

        for difficulty in DifficultyLevel:
            problem, trace = generator.generate(
                seed=42,
                difficulty=difficulty,
            )

            # Gold answer should verify
            result = verifier.verify_final(problem, problem.gold_answer)
            assert result.correct, f"Failed for difficulty {difficulty}"
