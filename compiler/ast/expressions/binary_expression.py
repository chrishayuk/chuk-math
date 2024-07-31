from .expression import Expression

class BinaryExpression(Expression):
    def __init__(self, left, operator, right):
        super().__init__()

        self.left = left
        self.operator = operator
        self.right = right

    def __str__(self):
        # Use the operator's value directly for the symbol in the string representation
        return f"{self.left} {self.operator.value} {self.right}"
    
    def to_dict(self):
        # binary expression as a dictionary, handles recursion
        return {
            "type": "BinaryExpression",
            "operator": self.operator.value if hasattr(self.operator, 'value') else str(self.operator),
            "left": self.left.to_dict() if hasattr(self.left, 'to_dict') else str(self.left),
            "right": self.right.to_dict() if hasattr(self.right, 'to_dict') else str(self.right),
        }
