import pytest
from lexer.arithmetic_expression import ArithmeticExpression

def test_basic_expression():
    expression = "3 + 5 * (10 - -4.5)"
    parser = ArithmeticExpression(expression)
    expected_tokens = [
        {'type': 'number', 'value': 3.0, 'position': 0},
        {'type': 'operator', 'value': '+', 'position': 2},
        {'type': 'number', 'value': 5.0, 'position': 4},
        {'type': 'operator', 'value': '*', 'position': 6},
        {'type': 'parenthesis', 'value': '(', 'position': 8},
        {'type': 'number', 'value': 10.0, 'position': 9},
        {'type': 'operator', 'value': '-', 'position': 12},
        {'type': 'number', 'value': -4.5, 'position': 14},
        {'type': 'parenthesis', 'value': ')', 'position': 18}
    ]
    tokens = parser.parse()
    assert tokens == expected_tokens

def test_parse_as_json():
    import json
    expression = "3 + 5 * (10 - 4)"
    parser = ArithmeticExpression(expression)
    expected_json = {
        "tokens": [
            {"type": "number", "value": 3.0, "position": 0},
            {"type": "operator", "value": "+", "position": 2},
            {"type": "number", "value": 5.0, "position": 4},
            {"type": "operator", "value": "*", "position": 6},
            {"type": "parenthesis", "value": "(", "position": 8},
            {"type": "number", "value": 10.0, "position": 9},
            {"type": "operator", "value": "-", "position": 12},
            {"type": "number", "value": 4.0, "position": 14},
            {"type": "parenthesis", "value": ")", "position": 15}
        ]
    }
    json_output = parser.parse_as_json()
    assert json_output == json.dumps(expected_json, indent=2)

def test_empty_expression():
    expression = ""
    parser = ArithmeticExpression(expression)
    expected_tokens = []
    tokens = parser.parse()
    assert tokens == expected_tokens

def test_invalid_expression():
    expression = "3 + * 5"
    parser = ArithmeticExpression(expression)
    with pytest.raises(ValueError):
        parser.parse()
