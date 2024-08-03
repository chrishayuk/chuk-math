import random

def generate_random_operator(include_advanced_operators=False, allow_division=True):
    """
    Generate a random operator based on the specified options.
    
    Parameters:
    - include_advanced_operators (bool): If True, include advanced operators like '%' and '**'.
    - allow_division (bool): If False, exclude the division operator '/'.

    Returns:
    - str: Randomly selected operator.
    """
    basic_operators = ["+", "-", "*", "/"]

    # check if we're allowing division
    if not allow_division:
        # remove division if not supporting
        basic_operators.remove("/")

    # set the advanced operators
    advanced_operators = ["%", "**"] if include_advanced_operators else []

    # add basic operators and advanced operators together
    operators = basic_operators + advanced_operators

    # return the random operator
    return random.choice(operators)
