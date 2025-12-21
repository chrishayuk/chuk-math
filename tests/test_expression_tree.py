import pytest

from chuk_math_gym.explanations.expression_node import ExpressionNode
from chuk_math_gym.explanations.expression_tree import ExpressionTree


def test_print_tree():
    root = ExpressionNode("+", ExpressionNode("3"), ExpressionNode("7"))
    tree = ExpressionTree()
    tree.root = root

    expected_output = "+\n    |-- 3\n    |-- 7\n"
    assert tree.print_tree(tree.root).strip() == expected_output.strip()


def test_expression_tree_init():
    """Test ExpressionTree initialization."""
    tree = ExpressionTree()
    assert tree.root is None


def test_expression_tree_evaluate():
    """Test evaluate method."""
    tree = ExpressionTree()
    tree.root = ExpressionNode("+", ExpressionNode("3"), ExpressionNode("5"))
    result = tree.evaluate(0)
    assert result == 8.0


def test_expression_tree_evaluate_empty():
    """Test evaluate with empty tree raises error."""
    tree = ExpressionTree()
    with pytest.raises(ValueError, match="Cannot evaluate empty tree"):
        tree.evaluate(0)


def test_print_tree_empty():
    """Test print_tree with None node."""
    tree = ExpressionTree()
    result = tree.print_tree(None)
    assert result == ""


def test_print_tree_nested():
    """Test print_tree with nested expression."""
    # (3 + 5) * 2
    left = ExpressionNode("+", ExpressionNode("3"), ExpressionNode("5"))
    tree = ExpressionTree()
    tree.root = ExpressionNode("*", left, ExpressionNode("2"))

    result = tree.print_tree(tree.root)
    assert "*" in result
    assert "+" in result
    assert "3" in result
    assert "5" in result
    assert "2" in result
