import random
from expression_generator.utilities.random_number_generator import generate_random_number
from expression_generator.utilities.random_operator_generator import generate_random_operator

def format_number(num: float, decimal_places: int = 2) -> str:
    """
    Convert 'num' to a string truncated to 'decimal_places' decimals,
    *without* wrapping negative values in parentheses anymore.
    
    Examples:
      -  -6142  -> "-6142"
      -  -12.34 -> "-12.34"
      -  45     -> "45"
      -  3.14159 -> "3.14"
    """
    if decimal_places > 0:
        num = round(num, decimal_places)
        s = f"{num:.{decimal_places}f}"  # exact decimals
    else:
        # no decimals → integer
        num = round(num)
        s = str(int(num))

    return s  # negative numbers are just e.g. "-6142"

def needs_parens(expr: str) -> bool:
    """
    Decide if we *might* want parentheses around 'expr'.
    We do this if 'expr' contains operators/spaces or is more than a single token.
    """
    # If expr looks like a simple number (possibly negative), skip parentheses:
    # e.g. "-6142" or "3.14" or "42"
    # We'll add parentheses only if we detect +, -, *, /, or spaces beyond a leading minus.
    
    # Remove leading/trailing whitespace
    expr = expr.strip()

    # If it starts with a minus but has no additional operators/spaces, it's a single negative literal
    if expr.startswith('-'):
        # if there's another operator or space inside, we might still want parentheses
        # but if it's purely '-####' or '-####.##', skip
        # check if there's a space or +,*,/ beyond the first char
        if any(op in expr[1:] for op in ['+', '-', '*', '/', ' ']):
            return True
        return False

    # For non-negative, check if it has spaces or an operator
    operators = ['+', '-', '*', '/']
    if any(op in expr for op in operators) or ' ' in expr:
        return True
    return False

def maybe_wrap(expr: str, chance: float = 0.5) -> str:
    """
    Randomly wrap expr in parentheses if 'needs_parens(expr)' is True, with 'chance' probability.
    """
    expr = expr.strip()
    if needs_parens(expr) and random.random() < chance:
        return f"({expr})"
    return expr

class ArithmeticExpressionGenerator:
    def __init__(self):
        pass

    def generate_expression(
        self,
        depth: int = 0,
        max_depth: int = 2,
        allow_negative: bool = True,
        allow_decimals: bool = True,
        min_number: float = 1,
        max_number: float = 10,
        include_advanced_operators: bool = False,
        allow_division: bool = True,
        decimal_places: int = 2
    ) -> str:
        """
        Recursively generate a random mathematical expression.
        """
        # Decide whether to produce a leaf (just a number) or form a subexpression
        if depth > max_depth or random.random() < (1 - depth / max_depth):
            val = generate_random_number(
                min_val=min_number,
                max_val=max_number,
                allow_negative=allow_negative,
                allow_decimals=allow_decimals,
                decimal_places=decimal_places
            )
            return format_number(val, decimal_places)
        else:
            operator = generate_random_operator(include_advanced_operators, allow_division)

            # For '/', force integer mode on both sides
            if operator == "/":
                left_decimals = right_decimals = False
            else:
                left_decimals = right_decimals = allow_decimals

            left_part = self.generate_expression(
                depth=depth + 1,
                max_depth=max_depth,
                allow_negative=allow_negative,
                allow_decimals=left_decimals,
                min_number=min_number,
                max_number=max_number,
                include_advanced_operators=include_advanced_operators,
                allow_division=allow_division,
                decimal_places=decimal_places
            )

            right_val = generate_random_number(
                min_val=1,
                max_val=10,
                allow_negative=allow_negative,
                allow_decimals=right_decimals,
                decimal_places=decimal_places
            )
            # Avoid dividing by zero
            if operator == "/" and right_val == 0:
                right_val = generate_random_number(
                    min_val=1,
                    max_val=10,
                    allow_negative=False,
                    allow_decimals=False
                )

            right_part = format_number(right_val, decimal_places)

            # Maybe wrap each side if they contain operators/spaces
            left_part = maybe_wrap(left_part, 0.6)   # 60% chance
            right_part = maybe_wrap(right_part, 0.6) # 60% chance

            expr = f"{left_part} {operator} {right_part}"

            # Randomly wrap the entire subexpression
            expr = maybe_wrap(expr, 0.7)  # 70% chance

            return expr

    def generate_random_expression(self, difficulty: str) -> str:
        """
        Generate a random mathematical expression based on the difficulty level.
        """
        if difficulty == "very easy":
            max_depth, base_operands = 1, 2
            allow_negative, allow_decimals = False, False
            min_number, max_number = 1, 100
            include_advanced_operators, allow_division = False, False
            decimal_places = 0
        elif difficulty == "easy":
            max_depth, base_operands = 1, 2
            allow_negative, allow_decimals = False, False
            min_number, max_number = 1, 1000
            include_advanced_operators, allow_division = False, False
            decimal_places = 0
        elif difficulty == "pretty easy":
            max_depth, base_operands = 1, 3
            allow_negative, allow_decimals = True, False
            min_number, max_number = -1000, 1000
            include_advanced_operators, allow_division = False, True
            decimal_places = 0
        elif difficulty == "medium":
            max_depth, base_operands = 2, 3
            allow_negative, allow_decimals = True, False
            min_number, max_number = -10000, 10000
            include_advanced_operators, allow_division = False, True
            decimal_places = 0
        elif difficulty == "hard":
            max_depth, base_operands = 2, 4
            allow_negative, allow_decimals = True, True
            min_number, max_number = -100000, 100000
            include_advanced_operators, allow_division = False, True
            decimal_places = 3
        elif difficulty == "pretty hard":
            max_depth, base_operands = 3, 4
            allow_negative, allow_decimals = True, True
            min_number, max_number = -500000, 500000
            include_advanced_operators, allow_division = False, True
            decimal_places = 4
        elif difficulty == "very hard":
            max_depth, base_operands = 3, 5
            allow_negative, allow_decimals = True, True
            min_number, max_number = -1000000, 1000000
            include_advanced_operators, allow_division = False, True
            decimal_places = 4
        else:
            raise ValueError(f"Unknown difficulty level: {difficulty}")

        expression = self.generate_expression(
            depth=0,
            max_depth=max_depth,
            allow_negative=allow_negative,
            allow_decimals=allow_decimals,
            min_number=min_number,
            max_number=max_number,
            include_advanced_operators=include_advanced_operators,
            allow_division=allow_division,
            decimal_places=decimal_places
        )

        # If the difficulty suggests multiple operands, chain them
        number_of_operands = base_operands + random.randint(0, 1)
        for _ in range(1, number_of_operands):
            operator = generate_random_operator(include_advanced_operators, allow_division)

            # If '/', force integer mode
            if operator == "/":
                next_decimals = False
            else:
                next_decimals = allow_decimals

            new_expr = self.generate_expression(
                depth=0,
                max_depth=max_depth,
                allow_negative=allow_negative,
                allow_decimals=next_decimals,
                min_number=min_number,
                max_number=max_number,
                include_advanced_operators=include_advanced_operators,
                allow_division=allow_division,
                decimal_places=decimal_places
            )

            chained = f"{expression} {operator} {new_expr}"
            # Randomly wrap the combined expression
            chained = maybe_wrap(chained, 0.4)  # 40% chance

            expression = chained

        return expression
