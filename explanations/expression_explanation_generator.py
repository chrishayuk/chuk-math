from explanations.expression_node import ExpressionNode

class ExpressionExplanationGenerator:
    def __init__(self, root: ExpressionNode):
        self.root = root
        self.explanations = []

    def generate_explanation(self, missing_element: float) -> str:
        self.explanations = []  # Reset explanations
        result = self._evaluate_and_explain(self.root, missing_element)
        return "\n".join(self.explanations), result

    def _evaluate_and_explain(self, node: ExpressionNode, missing_element: float) -> float:
        if node.value == '?':
            explanation = f"? = {missing_element}"
            self.explanations.append(f"STEP {len(self.explanations)}: {explanation}")
            return missing_element

        if not node.left and not node.right:
            return float(node.value)

        left_value = self._evaluate_and_explain(node.left, missing_element) if node.left else 0
        right_value = self._evaluate_and_explain(node.right, missing_element) if node.right else 0

        result = self._perform_calculation(node.value, left_value, right_value)
        rounded_result_for_display = self._round_result_for_display(result)

        # Generate explanation with simplified expression
        left_display = self._format_number_for_display(left_value)
        right_display = self._format_number_for_display(right_value)
        explanation = f"({left_display} {node.value} {right_display}) = {rounded_result_for_display}"
        self.explanations.append(f"STEP {len(self.explanations)}: {explanation}")

        return result

    def _perform_calculation(self, operator: str, left_value: float, right_value: float) -> float:
        if operator == '+':
            return left_value + right_value
        if operator == '-':
            return left_value - right_value
        if operator == '*':
            return left_value * right_value
        if operator == '/':
            return left_value / right_value
        raise ValueError(f"Unknown operator: {operator}")

    def _round_result_for_display(self, num: float) -> str:
        rounded_number = round(num, 4)
        return str(int(rounded_number)) if rounded_number.is_integer() else str(rounded_number)

    def _format_number_for_display(self, num: float) -> str:
        return str(int(num)) if num.is_integer() else str(num)
