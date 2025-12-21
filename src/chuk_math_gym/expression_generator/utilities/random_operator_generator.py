import random

def generate_random_operator(include_advanced_operators=False, allow_division=True):
    """
    Generate a random operator based on the specified options.
    """
    basic_operators = ["+", "-", "*", "/"]
    
    # Remove '/' if we do not allow division
    if not allow_division and "/" in basic_operators:
        basic_operators.remove("/")

    # For now, do NOT include advanced operators because the parser doesn't handle them.
    # advanced_operators = ["%", "**"]  # uncomment later if the parser is updated
    advanced_operators = []  # keep empty to avoid parser errors
    
    if include_advanced_operators:
        # If the parser is ready, you could do:
        # advanced_operators = ["%", "**"]
        pass

    operators = basic_operators + advanced_operators
    return random.choice(operators)