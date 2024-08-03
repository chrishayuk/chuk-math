import random
from utilities.random_number_generator import generate_random_number
from utilities.random_operator_generator import generate_random_operator

class ExpressionGenerator:
    def __init__(self):
        pass

    def generate_expression(self, depth: int = 0, max_depth: int = 2, allow_negative: bool = True, allow_decimals: bool = True, 
                            min_number: float = 1, max_number: float = 10, include_advanced_operators: bool = False, 
                            allow_division: bool = True) -> str:
        """
        Recursively generate a random mathematical expression.
        
        Parameters:
        - depth (int): Current depth of the recursive generation.
        - max_depth (int): Maximum depth allowed for recursion.
        - allow_negative (bool): If True, numbers can be negative.
        - allow_decimals (bool): If True, numbers can be decimals.
        - min_number (float): Minimum number in the expressions.
        - max_number (float): Maximum number in the expressions.
        - include_advanced_operators (bool): If True, include advanced operators like '%' and '**'.
        - allow_division (bool): If True, division can be used in the expressions.

        Returns:
        - str: A randomly generated expression as a string.
        """
        if depth > max_depth or random.random() < (1 - depth / max_depth):
            return str(generate_random_number(min_number, max_number, allow_negative, allow_decimals))
        else:
            operator = generate_random_operator(include_advanced_operators, allow_division)
            left_part = self.generate_expression(depth + 1, max_depth, allow_negative, allow_decimals, min_number, max_number, include_advanced_operators, allow_division)

            right_part = generate_random_number(1, 10, allow_negative, allow_decimals and operator != "/")
            if operator == "/" and right_part == 0:
                right_part = generate_random_number(1, 10, False, False)

            expression = f"({left_part} {operator} {right_part})" if random.random() < 0.7 else f"{left_part} {operator} {right_part}"
            return expression

    def generate_random_expression(self, difficulty: str) -> str:
        """
        Generate a random mathematical expression based on the difficulty level.
        
        Parameters:
        - difficulty (str): The difficulty level of the expression ("very easy", "easy", etc.).

        Returns:
        - str: A randomly generated expression as a string.
        """
        if difficulty == "very easy":
            max_depth, base_operands, allow_negative, allow_decimals, min_number, max_number = 1, 2, False, False, 1, 100
            include_advanced_operators, allow_division = False, False
        elif difficulty == "easy":
            max_depth, base_operands, allow_negative, allow_decimals, min_number, max_number = 1, 2, False, False, 1, 1000
            include_advanced_operators, allow_division = False, False
        elif difficulty == "pretty easy":
            max_depth, base_operands, allow_negative, allow_decimals, min_number, max_number = 1, 3, True, False, -1000, 1000
            include_advanced_operators, allow_division = False, True
        elif difficulty == "medium":
            max_depth, base_operands, allow_negative, allow_decimals, min_number, max_number = 2, 3, True, False, -10000, 10000
            include_advanced_operators, allow_division = False, True
        elif difficulty == "hard":
            max_depth, base_operands, allow_negative, allow_decimals, min_number, max_number = 2, 4, True, True, -100000, 100000
            include_advanced_operators, allow_division = True, True
        elif difficulty == "pretty hard":
            max_depth, base_operands, allow_negative, allow_decimals, min_number, max_number = 3, 4, True, True, -500000, 500000
            include_advanced_operators, allow_division = True, True
        elif difficulty == "very hard":
            max_depth, base_operands, allow_negative, allow_decimals, min_number, max_number = 3, 5, True, True, -1000000, 1000000
            include_advanced_operators, allow_division = True, True
        else:
            raise ValueError(f"Unknown difficulty level: {difficulty}")
        
        # generate the number of operands
        number_of_operands = base_operands + random.randint(0, 1)

        # generate the expression
        expression = self.generate_expression(0, max_depth, allow_negative, allow_decimals, min_number, max_number, include_advanced_operators, allow_division)
        
        # loop through the operands
        for _ in range(1, number_of_operands):
            # generate an operator
            operator = generate_random_operator(include_advanced_operators, allow_division)

            # generate an expression
            new_expression = self.generate_expression(0, max_depth, allow_negative, allow_decimals, min_number, max_number, include_advanced_operators, allow_division)

            # add the expression
            expression += f" {operator} {new_expression}"

        # return the expression
        return expression


# Example usage
if __name__ == "__main__":
    # setup the generator
    eg = ExpressionGenerator()

    # generate some random expressions
    print(eg.generate_random_expression("very easy"))
