import random

def generate_random_number(min=1, max=10, allow_negative=False, allow_decimals=False, decimal_places=2):
    """
    Generate a random number with specified options.
    
    Parameters:
    - min (int/float): Minimum value for the random number.
    - max (int/float): Maximum value for the random number.
    - allow_negative (bool): If True, the number can be negative.
    - allow_decimals (bool): If True, the number can be a decimal.
    - decimal_places (int): Number of decimal places if allow_decimals is True.

    Returns:
    - float/int: Generated random number.
    """
    
    # check if we're allowing decimals
    if allow_decimals:
        # generate a decimal
        number = random.uniform(min, max)

        # round the number
        number = round(number, decimal_places)
    else:
        # generate an integer
        number = random.randint(min, max)
    
    # check we're allowing negative
    if allow_negative and random.random() < 0.5:
        # set the number as negative
        number = -number

    # return the number
    return number
