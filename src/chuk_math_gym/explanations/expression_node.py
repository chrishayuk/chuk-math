from typing import Union, List

class ExpressionNode:
    def __init__(self, value: str, left: 'ExpressionNode' = None, right: 'ExpressionNode' = None):
        self.value = value
        self.left = left
        self.right = right

    def evaluate(self, missing_element: float) -> float:
        if self.value == '?':
            return missing_element

        if not self.left and not self.right:
            return float(self.value)

        left_value = self.left.evaluate(missing_element) if self.left else 0
        right_value = self.right.evaluate(missing_element) if self.right else 0

        return self._perform_calculation(left_value, right_value)

    def _perform_calculation(self, left_value: float, right_value: float) -> float:
        if self.value == '+':
            return left_value + right_value
        if self.value == '-':
            return left_value - right_value
        if self.value == '*':
            return left_value * right_value
        if self.value == '/':
            return left_value / right_value
        raise ValueError(f"Unknown operator: {self.value}")

