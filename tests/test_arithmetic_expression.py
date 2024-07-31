import pytest
from compiler.parser.arithmetic_expression import ArithmeticExpression

def test_basic_expression():
    expression = "3 + 5 * (10 - -4.5)"
    parser = ArithmeticExpression(expression)
    expected_tokens = [
        {'type': 'NUMBER', 'value': 3.0, 'position': 0},
        {'type': 'OPERATOR', 'value': '+', 'position': 2},
        {'type': 'NUMBER', 'value': 5.0, 'position': 4},
        {'type': 'OPERATOR', 'value': '*', 'position': 6},
        {'type': 'PARENTHESIS', 'value': '(', 'position': 8},
        {'type': 'NUMBER', 'value': 10.0, 'position': 9},
        {'type': 'OPERATOR', 'value': '-', 'position': 12},
        {'type': 'OPERATOR', 'value': '-', 'position': 14},
        {'type': 'NUMBER', 'value': 4.5, 'position': 15},
        {'type': 'PARENTHESIS', 'value': ')', 'position': 18}
    ]
    tokens = parser.parse()
    assert tokens == expected_tokens

def test_parse_as_json():
    import json
    expression = "3 + 5 * (10 - 4)"
    parser = ArithmeticExpression(expression)
    expected_json = {
        "tokens": [
            {"type": "NUMBER", "value": 3.0, "position": 0},
            {"type": "OPERATOR", "value": "+", "position": 2},
            {"type": "NUMBER", "value": 5.0, "position": 4},
            {"type": "OPERATOR", "value": "*", "position": 6},
            {"type": "PARENTHESIS", "value": "(", "position": 8},
            {"type": "NUMBER", "value": 10.0, "position": 9},
            {"type": "OPERATOR", "value": "-", "position": 12},
            {"type": "NUMBER", "value": 4.0, "position": 14},
            {"type": "PARENTHESIS", "value": ")", "position": 15}
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
