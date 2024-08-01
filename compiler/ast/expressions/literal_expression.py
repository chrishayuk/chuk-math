import decimal
from .expression import Expression

class Literal(Expression):
    def __init__(self, value):
        try:
            self.value = decimal.Decimal(value)
        except (ValueError, decimal.InvalidOperation):
            self.value = value

    def __str__(self):
        return str(self.value)
    
    def to_dict(self):
        # Check if the value is a Decimal instance
        if isinstance(self.value, decimal.Decimal):
            # Convert to integer if it's a whole number, float otherwise
            if self.value % 1 == 0:
                return {
                    "type": "LiteralExpression",
                    "value": int(self.value)
                }
            else:
                return {
                    "type": "LiteralExpression",
                    "value": float(self.value)
                }
        else:
            # Non-numeric values are returned as-is
            return {
                "type": "LiteralExpression",
                "value": self.value
            }
        
    def __eq__(self, other):
        if isinstance(other, Literal):
            return self.value == other.value
        return False
