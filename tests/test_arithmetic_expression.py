from decimal import Decimal
import pytest
from compiler.lexer.token import Token
from compiler.parser.arithmetic_expression import ArithmeticExpression
from compiler.ast.expressions import BinaryExpression, Literal, UnaryExpression
import json

def test_basic_expression():
    expression = "3 + 5 * (10 - -4.5)"
    parser = ArithmeticExpression(expression)
    ast = parser.parse()
    
    expected_ast = BinaryExpression(
        left=Literal(Decimal('3')),
        operator=Token('OPERATOR', '+', 2),
        right=BinaryExpression(
            left=Literal(Decimal('5')),
            operator=Token('OPERATOR', '*', 6),
            right=BinaryExpression(
                left=Literal(Decimal('10')),
                operator=Token('OPERATOR', '-', 12),
                right=UnaryExpression(
                    operator=Token('OPERATOR', '-', 14),
                    operand=Literal(Decimal('4.5'))
                )
            )
        )
    )

    assert ast == expected_ast, f"AST mismatch: expected {repr(expected_ast)}, got {repr(ast)}"



def test_parse_as_json():
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
    ast = parser.parse()
    assert ast is None  # Expecting None or a specific empty representation

def test_invalid_expression():
    expression = "3 + * 5"
    parser = ArithmeticExpression(expression)
    with pytest.raises(SyntaxError):  # Adjusted to SyntaxError
        parser.parse()

def test_unary_minus():
    expression = "-3"
    parser = ArithmeticExpression(expression)
    ast = parser.parse()

    expected_ast = UnaryExpression(
        operator=Token('OPERATOR', '-', 0),
        operand=Literal(Decimal('3'))
    )

    assert ast == expected_ast, f"AST mismatch: expected {repr(expected_ast)}, got {repr(ast)}"



