from explanations.expression_node import ExpressionNode
from explanations.expression_tree import ExpressionTree

def test_print_tree():
    root = ExpressionNode("+", ExpressionNode("3"), ExpressionNode("7"))
    tree = ExpressionTree()
    tree.root = root

    expected_output = (
        "+\n"
        "    |-- 3\n"
        "    |-- 7\n"
    )
    assert tree.print_tree(tree.root).strip() == expected_output.strip()
