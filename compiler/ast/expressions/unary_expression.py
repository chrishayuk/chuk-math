from .expression import Expression

class UnaryExpression(Expression):
    def __init__(self, operator, operand):
        self.operator = operator
        self.operand = operand

    def __eq__(self, other):
        if isinstance(other, UnaryExpression):
            if self.operator != other.operator:
                print(f"Operator mismatch: {self.operator} != {other.operator}")
            if self.operand != other.operand:
                print(f"Operand mismatch: {self.operand} != {other.operand}")
            return self.operator == other.operator and self.operand == other.operand
        return False

    def __repr__(self):
        return f"UnaryExpression(operator={repr(self.operator)}, operand={repr(self.operand)})"

    def to_dict(self):
        # unary expression as a dictionary, handles recursion
        return {
            "type": "UnaryExpression",
            "operator": self.operator.value if hasattr(self.operator, 'value') else str(self.operator),
            "operand": self.operand.to_dict() if hasattr(self.operand, 'to_dict') else str(self.operand),
        }
