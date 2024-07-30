
from explanations.expression_explanation_generator import ExpressionExplanationGenerator
from explanations.expression_node import ExpressionNode
from explanations.expression_tree import ExpressionTree

def main():
    # Building the expression: (3 + 5) * (10 - 4)
    root = ExpressionNode("*",
                          ExpressionNode("+", ExpressionNode("3"), ExpressionNode("5")),
                          ExpressionNode("-", ExpressionNode("10"), ExpressionNode("4")))

    # Create the expression tree
    tree = ExpressionTree()
    tree.root = root

    # Print the tree
    print("Expression Tree:")
    print(tree.print_tree(tree.root))

    # Evaluate the expression
    result = tree.evaluate(0)
    result_display = str(int(result)) if result.is_integer() else str(result)
    print(f"Result of the expression: {result_display}")

    # Generate explanation
    explanation_generator = ExpressionExplanationGenerator(root)
    explanation_text, final_result = explanation_generator.generate_explanation(0)
    print("Explanation of the steps:")
    print(explanation_text)

if __name__ == "__main__":
    main()