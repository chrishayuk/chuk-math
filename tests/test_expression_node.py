from chuk_math_gym.explanations.expression_explanation_generator import (
    ExpressionExplanationGenerator,
)
from chuk_math_gym.explanations.expression_node import ExpressionNode


def test_evaluate_simple_number():
    node = ExpressionNode("5")
    assert node.evaluate(0) == 5.0


def test_evaluate_with_missing_element():
    node = ExpressionNode("?")
    assert node.evaluate(42) == 42.0


def test_evaluate_addition():
    node = ExpressionNode("+", ExpressionNode("3"), ExpressionNode("7"))
    assert node.evaluate(0) == 10.0


def test_evaluate_multiplication():
    node = ExpressionNode("*", ExpressionNode("3"), ExpressionNode("7"))
    assert node.evaluate(0) == 21.0


def test_evaluate_complex_expression():
    node = ExpressionNode(
        "+",
        ExpressionNode("*", ExpressionNode("3"), ExpressionNode("7")),
        ExpressionNode("-", ExpressionNode("10"), ExpressionNode("2")),
    )
    assert node.evaluate(0) == 29.0


def test_evaluate_and_explain():
    node = ExpressionNode(
        "+", ExpressionNode("3"), ExpressionNode("*", ExpressionNode("2"), ExpressionNode("4"))
    )
    explanation_generator = ExpressionExplanationGenerator(node)
    explanation_text, result = explanation_generator.generate_explanation(0)
    expected_explanations = ["STEP 0: (2 * 4) = 8", "STEP 1: (3 + 8) = 11"]
    assert result == 11.0
    assert explanation_text.split("\n") == expected_explanations


def test_evaluate_subtraction():
    """Test subtraction operator."""
    node = ExpressionNode("-", ExpressionNode("10"), ExpressionNode("3"))
    assert node.evaluate(0) == 7.0


def test_evaluate_division():
    """Test division operator."""
    node = ExpressionNode("/", ExpressionNode("10"), ExpressionNode("2"))
    assert node.evaluate(0) == 5.0


def test_evaluate_unknown_operator():
    """Test unknown operator raises ValueError."""
    import pytest

    node = ExpressionNode("^", ExpressionNode("2"), ExpressionNode("3"))
    with pytest.raises(ValueError, match="Unknown operator"):
        node.evaluate(0)


class TestExpressionExplanationGenerator:
    """Tests for ExpressionExplanationGenerator edge cases."""

    def test_missing_element_placeholder(self):
        """Test explanation with missing element (?)."""
        node = ExpressionNode("+", ExpressionNode("?"), ExpressionNode("5"))
        gen = ExpressionExplanationGenerator(node)
        explanation, result = gen.generate_explanation(missing_element=10.0)

        assert result == 15.0
        assert "? = 10" in explanation

    def test_subtraction_explanation(self):
        """Test subtraction generates correct explanation."""
        node = ExpressionNode("-", ExpressionNode("10"), ExpressionNode("3"))
        gen = ExpressionExplanationGenerator(node)
        explanation, result = gen.generate_explanation(0)

        assert result == 7.0
        assert "(10 - 3) = 7" in explanation

    def test_division_explanation(self):
        """Test division generates correct explanation."""
        node = ExpressionNode("/", ExpressionNode("10"), ExpressionNode("2"))
        gen = ExpressionExplanationGenerator(node)
        explanation, result = gen.generate_explanation(0)

        assert result == 5.0
        assert "(10 / 2) = 5" in explanation

    def test_unknown_operator_in_explanation(self):
        """Test unknown operator raises error in explanation generator."""
        import pytest

        node = ExpressionNode("%", ExpressionNode("10"), ExpressionNode("3"))
        gen = ExpressionExplanationGenerator(node)
        with pytest.raises(ValueError, match="Unknown operator"):
            gen.generate_explanation(0)


class TestPlaceholderExpressionExplanationGenerator:
    """Tests for PlaceholderExpressionExplanationGenerator edge cases."""

    def test_missing_element_placeholder(self):
        """Test placeholder generation with missing element (?)."""
        from chuk_math_gym.explanations.expression_placeholder_explanation_generator import (
            PlaceholderExpressionExplanationGenerator,
        )

        node = ExpressionNode("+", ExpressionNode("?"), ExpressionNode("5"))
        gen = PlaceholderExpressionExplanationGenerator(node)
        result = gen.generate_explanation(missing_element=10.0)

        assert result["final_value"] == 15.0
        assert "? = 10" in str(result["real_steps"])

    def test_operator_missing_left_child(self):
        """Test operator node missing left child raises error."""
        import pytest

        from chuk_math_gym.explanations.expression_placeholder_explanation_generator import (
            PlaceholderExpressionExplanationGenerator,
        )

        node = ExpressionNode("+", None, ExpressionNode("5"))
        gen = PlaceholderExpressionExplanationGenerator(node)
        with pytest.raises(ValueError, match="missing left child"):
            gen.generate_explanation(0)

    def test_operator_missing_right_child(self):
        """Test operator node missing right child raises error."""
        import pytest

        from chuk_math_gym.explanations.expression_placeholder_explanation_generator import (
            PlaceholderExpressionExplanationGenerator,
        )

        # Create node with left but no right
        node = ExpressionNode("+")
        node.left = ExpressionNode("3")
        node.right = None

        gen = PlaceholderExpressionExplanationGenerator(node)
        with pytest.raises(ValueError, match="missing right child"):
            gen.generate_explanation(0)

    def test_unknown_operator_in_placeholder(self):
        """Test unknown operator raises error."""
        import pytest

        from chuk_math_gym.explanations.expression_placeholder_explanation_generator import (
            PlaceholderExpressionExplanationGenerator,
        )

        node = ExpressionNode("^", ExpressionNode("2"), ExpressionNode("3"))
        gen = PlaceholderExpressionExplanationGenerator(node)
        with pytest.raises(ValueError, match="Unknown operator"):
            gen.generate_explanation(0)

    def test_all_operators(self):
        """Test all four basic operators."""
        from chuk_math_gym.explanations.expression_placeholder_explanation_generator import (
            PlaceholderExpressionExplanationGenerator,
        )

        # Test subtraction
        node_sub = ExpressionNode("-", ExpressionNode("10"), ExpressionNode("3"))
        gen_sub = PlaceholderExpressionExplanationGenerator(node_sub)
        result_sub = gen_sub.generate_explanation(0)
        assert result_sub["final_value"] == 7.0

        # Test multiplication
        node_mul = ExpressionNode("*", ExpressionNode("3"), ExpressionNode("4"))
        gen_mul = PlaceholderExpressionExplanationGenerator(node_mul)
        result_mul = gen_mul.generate_explanation(0)
        assert result_mul["final_value"] == 12.0

        # Test division
        node_div = ExpressionNode("/", ExpressionNode("10"), ExpressionNode("2"))
        gen_div = PlaceholderExpressionExplanationGenerator(node_div)
        result_div = gen_div.generate_explanation(0)
        assert result_div["final_value"] == 5.0


class TestTraceGeneratorAbstract:
    """Tests for TraceGenerator abstract base class."""

    def test_cannot_instantiate_abstract_class(self):
        """Test that TraceGenerator cannot be instantiated directly."""
        import pytest

        from chuk_math_gym.trace.generator import TraceGenerator

        with pytest.raises(TypeError):
            TraceGenerator()

    def test_concrete_implementation(self):
        """Test that a concrete implementation works."""
        from chuk_math_gym.schemas.problem import DifficultyLevel, DomainType, Problem
        from chuk_math_gym.schemas.trace import Step, StepOperation, Trace
        from chuk_math_gym.trace.generator import TraceGenerator

        class ConcreteTraceGenerator(TraceGenerator):
            def generate(self, problem: Problem) -> Trace:
                return Trace(
                    problem_id=problem.id,
                    steps=[
                        Step(
                            index=0,
                            operation=StepOperation.EVAL,
                            before_state="test",
                            after_state="test",
                            output_value=1.0,
                        )
                    ],
                )

            def generate_from_expression(self, expression: str, problem_id: str) -> Trace:
                return Trace(
                    problem_id=problem_id,
                    steps=[
                        Step(
                            index=0,
                            operation=StepOperation.EVAL,
                            before_state=expression,
                            after_state="result",
                            output_value=1.0,
                        )
                    ],
                )

        gen = ConcreteTraceGenerator()
        problem = Problem(
            id="test",
            seed=0,
            domain=DomainType.ARITHMETIC,
            difficulty=DifficultyLevel.EASY,
            prompt="test",
            expression="3+5",
            gold_answer="8",
        )

        trace = gen.generate(problem)
        assert trace.problem_id == "test"

        trace2 = gen.generate_from_expression("3+5", "test2")
        assert trace2.problem_id == "test2"
