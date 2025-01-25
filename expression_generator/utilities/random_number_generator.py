# expression_generator/utilities/random_number_generator.py
import random

def generate_random_number(
    min_val=1,
    max_val=10,
    allow_negative=False,
    allow_decimals=False,
    decimal_places=2
):
    """
    Generate a random number with specified options.
    
    Parameters:
    - min_val (float): Minimum possible value
    - max_val (float): Maximum possible value
    - allow_negative (bool): If True, the number can be negative
    - allow_decimals (bool): If True, the number can be a float
    - decimal_places (int): Number of decimal digits to keep
    """
    if allow_decimals:
        # Generate a float, then round to the desired number of decimal places
        number = random.uniform(min_val, max_val)
        number = round(number, decimal_places)
    else:
        # Generate an integer
        number = random.randint(int(min_val), int(max_val))

    # Possibly flip sign to negative
    if allow_negative and random.random() < 0.5:
        number = -number

    return number
