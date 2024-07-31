from .expression import Expression

class UnaryExpression(Expression):
    def __init__(self, operator, operand):
        self.operator = operator
        self.operand = operand

    def to_dict(self):
        # unary expression as a dictionary, handles recursion
        return {
            "type": "UnaryExpression",
            "operator": self.operator.value if hasattr(self.operator, 'value') else str(self.operator),
            "operand": self.operand.to_dict() if hasattr(self.operand, 'to_dict') else str(self.operand),
        }
