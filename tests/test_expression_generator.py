import pytest
from utilities.random_number_generator import generate_random_number
from utilities.random_operator_generator import generate_random_operator
from expression_generator import ExpressionGenerator

def test_generate_random_number_integer():
    result = generate_random_number(1, 10, allow_negative=False, allow_decimals=False)
    assert isinstance(result, int)
    assert 1 <= result <= 10

def test_generate_random_number_negative():
    result = generate_random_number(1, 10, allow_negative=True, allow_decimals=False)
    assert isinstance(result, int)
    assert -10 <= result <= 10

def test_generate_random_number_decimal():
    result = generate_random_number(1, 10, allow_negative=False, allow_decimals=True, decimal_places=3)
    assert isinstance(result, float)
    assert 1 <= result <= 10
    assert round(result, 3) == result  # Ensures proper decimal precision

def test_generate_random_operator_basic():
    operators = {"+", "-", "*", "/"}
    result = generate_random_operator(include_advanced_operators=False, allow_division=True)
    assert result in operators

def test_generate_random_operator_no_division():
    operators = {"+", "-", "*"}
    result = generate_random_operator(include_advanced_operators=False, allow_division=False)
    assert result in operators

def test_generate_random_operator_advanced():
    operators = {"+", "-", "*", "/", "%", "**"}
    result = generate_random_operator(include_advanced_operators=True, allow_division=True)
    assert result in operators

def test_generate_expression_very_easy():
    eg = ExpressionGenerator()
    expression = eg.generate_random_expression("very easy")
    assert isinstance(expression, str)
    # For very easy, expressions should be simple, check that it does not contain advanced operators
    assert not any(op in expression for op in ["%", "**"])

def test_generate_expression_easy():
    eg = ExpressionGenerator()
    expression = eg.generate_random_expression("easy")
    assert isinstance(expression, str)
    assert not any(op in expression for op in ["%", "**"])

def test_generate_expression_medium():
    eg = ExpressionGenerator()
    expression = eg.generate_random_expression("medium")
    assert isinstance(expression, str)

def test_generate_expression_hard():
    eg = ExpressionGenerator()
    expression = eg.generate_random_expression("hard")
    assert isinstance(expression, str)
    assert any(op in expression for op in ["+", "-", "*", "/"])

def test_generate_expression_very_hard():
    eg = ExpressionGenerator()
    expression = eg.generate_random_expression("very hard")
    assert isinstance(expression, str)
    # Verify inclusion of possible advanced operators
    assert any(op in expression for op in ["%", "**", "+", "-", "*", "/"])
