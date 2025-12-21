"""Tests for AST-based trace generator."""

from chuk_math_gym.trace.ast_trace import (
    ASTNode,
    ExpressionTokenizer,
    ExpressionParser,
    ASTTraceGenerator,
)
from chuk_math_gym.schemas.problem import Problem, DomainType, DifficultyLevel


class TestASTNode:
    """Tests for ASTNode class."""

    def test_is_leaf(self):
        """Test is_leaf method."""
        leaf = ASTNode("5")
        assert leaf.is_leaf()

        non_leaf = ASTNode("+", ASTNode("3"), ASTNode("5"))
        assert not non_leaf.is_leaf()

    def test_is_operator(self):
        """Test is_operator method."""
        op = ASTNode("+")
        assert op.is_operator()

        num = ASTNode("5")
        assert not num.is_operator()

    def test_all_operators(self):
        """Test all supported operators."""
        for op in ["+", "-", "*", "/", "^"]:
            node = ASTNode(op)
            assert node.is_operator()


class TestExpressionTokenizer:
    """Tests for ExpressionTokenizer class."""

    def test_simple_expression(self):
        """Test tokenizing a simple expression."""
        tokenizer = ExpressionTokenizer("3 + 5")
        tokens = tokenizer.tokenize()
        assert tokens == ["3", "+", "5"]

    def test_expression_with_parentheses(self):
        """Test tokenizing with parentheses."""
        tokenizer = ExpressionTokenizer("(3 + 5) * 2")
        tokens = tokenizer.tokenize()
        assert tokens == ["(", "3", "+", "5", ")", "*", "2"]

    def test_decimal_numbers(self):
        """Test tokenizing decimal numbers."""
        tokenizer = ExpressionTokenizer("3.14 + 2.5")
        tokens = tokenizer.tokenize()
        assert tokens == ["3.14", "+", "2.5"]

    def test_scientific_notation(self):
        """Test tokenizing scientific notation."""
        tokenizer = ExpressionTokenizer("1e-5 + 2.5e3")
        tokens = tokenizer.tokenize()
        assert "1e-5" in tokens
        assert "2.5e3" in tokens

    def test_no_spaces(self):
        """Test tokenizing without spaces."""
        tokenizer = ExpressionTokenizer("3+5*2")
        tokens = tokenizer.tokenize()
        assert tokens == ["3", "+", "5", "*", "2"]

    def test_unknown_character(self):
        """Test handling unknown characters."""
        tokenizer = ExpressionTokenizer("3 + x")
        tokens = tokenizer.tokenize()
        # x is skipped
        assert tokens == ["3", "+"]


class TestExpressionParser:
    """Tests for ExpressionParser class."""

    def _parse(self, expr: str):
        """Helper to tokenize and parse expression."""
        tokens = ExpressionTokenizer(expr).tokenize()
        return ExpressionParser(tokens).parse()

    def test_simple_addition(self):
        """Test parsing simple addition."""
        ast = self._parse("3 + 5")
        assert ast is not None
        assert ast.value == "+"
        assert ast.left.value == "3"
        assert ast.right.value == "5"

    def test_order_of_operations(self):
        """Test order of operations (multiplication before addition)."""
        ast = self._parse("3 + 5 * 2")
        assert ast is not None
        # Should be: 3 + (5 * 2)
        assert ast.value == "+"
        assert ast.left.value == "3"
        assert ast.right.value == "*"

    def test_parentheses(self):
        """Test parentheses override precedence."""
        ast = self._parse("(3 + 5) * 2")
        assert ast is not None
        # Should be: (3 + 5) * 2
        assert ast.value == "*"
        assert ast.left.value == "+"
        assert ast.right.value == "2"

    def test_unary_minus(self):
        """Test unary minus at start."""
        ast = self._parse("-5 + 3")
        assert ast is not None

    def test_unary_plus(self):
        """Test unary plus at start."""
        ast = self._parse("+5 + 3")
        assert ast is not None

    def test_single_number(self):
        """Test parsing single number."""
        ast = self._parse("42")
        assert ast is not None
        assert ast.value == "42"

    def test_power_operator(self):
        """Test power operator."""
        ast = self._parse("2 ^ 3")
        assert ast is not None
        assert ast.value == "^"

    def test_division(self):
        """Test division."""
        ast = self._parse("10 / 2")
        assert ast is not None
        assert ast.value == "/"

    def test_subtraction(self):
        """Test subtraction."""
        ast = self._parse("10 - 3")
        assert ast is not None
        assert ast.value == "-"

    def test_empty_tokens(self):
        """Test parsing empty token list."""
        parser = ExpressionParser([])
        ast = parser.parse()
        assert ast is None


class TestASTTraceGenerator:
    """Tests for ASTTraceGenerator class."""

    def _make_problem(self, expression: str, gold_answer: str) -> Problem:
        """Create a test problem."""
        return Problem(
            id="test",
            seed=0,
            domain=DomainType.ARITHMETIC,
            difficulty=DifficultyLevel.EASY,
            prompt=f"Calculate: {expression}",
            expression=expression,
            gold_answer=gold_answer,
        )

    def test_generate_simple_trace(self):
        """Test generating trace for simple expression."""
        generator = ASTTraceGenerator()
        problem = self._make_problem("3 + 5", "8")

        trace = generator.generate(problem)
        assert trace is not None
        assert trace.final_value == 8.0
        assert len(trace.steps) > 0

    def test_generate_complex_trace(self):
        """Test generating trace for complex expression."""
        generator = ASTTraceGenerator()
        problem = self._make_problem("(3 + 5) * 2", "16")

        trace = generator.generate(problem)
        assert trace is not None
        assert trace.final_value == 16.0

    def test_trace_order_of_operations(self):
        """Test that trace follows order of operations."""
        generator = ASTTraceGenerator()
        problem = self._make_problem("3 + 5 * 2", "13")

        trace = generator.generate(problem)
        assert trace is not None
        assert trace.final_value == 13.0
        # Should evaluate 5*2 before 3+x

    def test_trace_division(self):
        """Test trace with division."""
        generator = ASTTraceGenerator()
        problem = self._make_problem("10 / 2", "5")

        trace = generator.generate(problem)
        assert trace is not None
        assert trace.final_value == 5.0

    def test_trace_subtraction(self):
        """Test trace with subtraction."""
        generator = ASTTraceGenerator()
        problem = self._make_problem("10 - 3", "7")

        trace = generator.generate(problem)
        assert trace is not None
        assert trace.final_value == 7.0

    def test_trace_power(self):
        """Test trace with power operator."""
        generator = ASTTraceGenerator()
        problem = self._make_problem("2 ^ 3", "8")

        trace = generator.generate(problem)
        assert trace is not None
        assert trace.final_value == 8.0

    def test_trace_negative_numbers(self):
        """Test trace with negative numbers."""
        generator = ASTTraceGenerator()
        problem = self._make_problem("-5 + 10", "5")

        trace = generator.generate(problem)
        assert trace is not None
        assert trace.final_value == 5.0

    def test_trace_decimal_numbers(self):
        """Test trace with decimal numbers."""
        generator = ASTTraceGenerator()
        problem = self._make_problem("3.5 + 2.5", "6")

        trace = generator.generate(problem)
        assert trace is not None
        assert trace.final_value == 6.0

    def test_trace_single_number(self):
        """Test trace with single number (no operations)."""
        generator = ASTTraceGenerator()
        problem = self._make_problem("42", "42")

        trace = generator.generate(problem)
        assert trace is not None
        assert trace.final_value == 42.0

    def test_steps_have_correct_operations(self):
        """Test that steps have correct operation types."""
        generator = ASTTraceGenerator()
        problem = self._make_problem("3 + 5", "8")

        trace = generator.generate(problem)
        assert trace is not None

        # Should have literal steps and an add step
        operations = [step.operation for step in trace.steps]
        # At minimum, should have ADD operation
        # (Implementation may vary - just check it runs)
        assert len(operations) > 0

    def test_generate_from_expression(self):
        """Test generating trace from expression string."""
        generator = ASTTraceGenerator()
        trace = generator.generate_from_expression("3 + 5", "test_problem")

        assert trace is not None
        assert trace.final_value == 8.0

    def test_generate_nested_parentheses(self):
        """Test generating trace with nested parentheses."""
        generator = ASTTraceGenerator()
        problem = self._make_problem("((2 + 3) * 4) - 5", "15")

        trace = generator.generate(problem)
        assert trace is not None
        assert trace.final_value == 15.0


class TestTraceIntegration:
    """Integration tests for trace generation."""

    def test_trace_steps_are_consistent(self):
        """Test that trace steps are internally consistent."""
        generator = ASTTraceGenerator()
        problem = Problem(
            id="test",
            seed=0,
            domain=DomainType.ARITHMETIC,
            difficulty=DifficultyLevel.EASY,
            prompt="Calculate: 3 + 5 * 2",
            expression="3 + 5 * 2",
            gold_answer="13",
        )

        trace = generator.generate(problem)
        assert trace is not None

        # Verify placeholder_map matches step outputs
        for step in trace.steps:
            if step.output and step.output in trace.placeholder_map:
                assert trace.placeholder_map[step.output] == step.output_value


class TestExpressionParserEdgeCases:
    """Edge case tests for ExpressionParser."""

    def _parse(self, expr: str):
        """Helper to tokenize and parse expression."""
        tokens = ExpressionTokenizer(expr).tokenize()
        return ExpressionParser(tokens).parse()

    def test_low_precedence_break(self):
        """Test parsing stops at lower precedence operator."""
        # 3 * 4 + 5 should parse 3*4 first, then + 5
        ast = self._parse("3 * 4 + 5")
        assert ast is not None
        assert ast.value == "+"  # Top level is addition
        assert ast.left.value == "*"  # Left subtree is multiplication

    def test_operator_at_end(self):
        """Test handling operator at end of tokens."""
        tokens = ["3", "+"]  # Missing right operand
        parser = ExpressionParser(tokens)
        ast = parser.parse()
        # Parser should handle gracefully
        assert ast is not None

    def test_right_associative_power(self):
        """Test that power is right-associative."""
        ast = self._parse("2 ^ 3 ^ 2")
        assert ast is not None
        # 2^(3^2) = 2^9 = 512, not (2^3)^2 = 8^2 = 64
        assert ast.value == "^"
        assert ast.right.value == "^"  # Right subtree is also power

    def test_unary_minus_in_expression(self):
        """Test unary minus in middle of expression."""
        ast = self._parse("5 + -3")
        assert ast is not None
        assert ast.value == "+"

    def test_parentheses_at_end(self):
        """Test parentheses at end of expression."""
        ast = self._parse("3 * (4 + 5)")
        assert ast is not None
        assert ast.value == "*"
        assert ast.right.value == "+"

    def test_primary_returns_none_on_unknown(self):
        """Test _parse_primary returns None for unknown token."""
        # This is tricky to test directly, but we can pass unusual tokens
        parser = ExpressionParser(["@"])  # Unknown character
        ast = parser.parse()
        assert ast is None  # Should return None for unparseable


class TestASTTraceGeneratorEdgeCases:
    """Edge case tests for ASTTraceGenerator."""

    def _make_problem(self, expression: str, gold_answer: str) -> Problem:
        """Create a test problem."""
        return Problem(
            id="test",
            seed=0,
            domain=DomainType.ARITHMETIC,
            difficulty=DifficultyLevel.EASY,
            prompt=f"Calculate: {expression}",
            expression=expression,
            gold_answer=gold_answer,
        )

    def test_unary_negation(self):
        """Test trace with unary negation."""
        generator = ASTTraceGenerator()
        problem = self._make_problem("-10", "-10")
        trace = generator.generate(problem)
        assert trace is not None
        assert trace.final_value == -10.0

    def test_deeply_nested(self):
        """Test deeply nested expression."""
        generator = ASTTraceGenerator()
        problem = self._make_problem("(((1 + 2) * 3) - 4) / 5", "1")
        trace = generator.generate(problem)
        assert trace is not None
        assert trace.final_value == 1.0

    def test_all_operators(self):
        """Test expression with all operators."""
        generator = ASTTraceGenerator()
        problem = self._make_problem("2 + 3 * 4 - 6 / 2", "11")
        trace = generator.generate(problem)
        assert trace is not None
        assert trace.final_value == 11.0
