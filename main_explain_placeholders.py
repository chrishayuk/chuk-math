from explanations.expression_explanation_generator import ExpressionExplanationGenerator
from explanations.expression_node import ExpressionNode
from explanations.expression_placeholder_explanation_generator import PlaceholderExpressionExplanationGenerator
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

    # Evaluate the expression normally
    result = tree.evaluate(0)
    result_display = str(int(result)) if result.is_integer() else str(result)
    print(f"Result of the expression: {result_display}")

    # Generate explanation using the PlaceholderExpressionExplanationGenerator
    explanation_generator = PlaceholderExpressionExplanationGenerator(root)
    explanation_data = explanation_generator.generate_explanation(missing_element=0)
    
    placeholder_steps = explanation_data["placeholder_steps"]
    real_steps = explanation_data["real_steps"]
    placeholder_map = explanation_data["placeholder_map"]
    placeholder_map_snapshots = explanation_data["placeholder_map_snapshots"]
    final_value = explanation_data["final_value"]

    # Print out the placeholder steps and placeholder map snapshots
    print("\n=== Explanation of the steps (Placeholder) ===")
    for i, step in enumerate(placeholder_steps):
        print("  " + step)
        
        # Print the snapshot for this step
        snapshot = placeholder_map_snapshots[i]
        print("  Current placeholder map after this step:")
        for ph, val in snapshot.items():
            print(f"    {ph} = {val}")
        print()  # blank line for readability

    # Print the real (numeric) steps
    print("\n=== Explanation of the steps (Real Values) ===")
    for step in real_steps:
        print("  " + step)

    # Print the final placeholder map
    print("\n=== Final Placeholder Map ===")
    for ph, val in placeholder_map.items():
        print(f"  {ph} = {val}")

    # Print the final numeric result
    print(f"\n=== Final Numeric Result: {final_value} ===")

if __name__ == "__main__":
    main()

