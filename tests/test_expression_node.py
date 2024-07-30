from explanations.expression_explanation_generator import ExpressionExplanationGenerator
from explanations.expression_node import ExpressionNode

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
    node = ExpressionNode("+",
                          ExpressionNode("*", ExpressionNode("3"), ExpressionNode("7")),
                          ExpressionNode("-", ExpressionNode("10"), ExpressionNode("2")))
    assert node.evaluate(0) == 29.0


def test_evaluate_and_explain():
    node = ExpressionNode("+",
                          ExpressionNode("3"),
                          ExpressionNode("*", ExpressionNode("2"), ExpressionNode("4")))
    explanation_generator = ExpressionExplanationGenerator(node)
    explanation_text, result = explanation_generator.generate_explanation(0)
    expected_explanations = [
        "STEP 0: (2 * 4) = 8",
        "STEP 1: (3 + 8) = 11"
    ]
    assert result == 11.0
    assert explanation_text.split("\n") == expected_explanations


