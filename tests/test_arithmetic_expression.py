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
        operator=Token('PLUS', '+', 2),
        right=BinaryExpression(
            left=Literal(Decimal('5')),
            operator=Token('MUL', '*', 6),
            right=BinaryExpression(
                left=Literal(Decimal('10')),
                operator=Token('MINUS', '-', 12),
                right=UnaryExpression(
                    operator=Token('MINUS', '-', 14),
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
        "left": {
            "value": "3",
            "type": "Literal"
        },
        "operator": {
            "type": "PLUS",
            "value": "+",
            "position": 2
        },
        "right": {
            "left": {
                "value": "5",
                "type": "Literal"
            },
            "operator": {
                "type": "MUL",
                "value": "*",
                "position": 6
            },
            "right": {
                "left": {
                    "value": "10",
                    "type": "Literal"
                },
                "operator": {
                    "type": "MINUS",
                    "value": "-",
                    "position": 12
                },
                "right": {
                    "value": "4",
                    "type": "Literal"
                },
                "type": "BinaryExpression"
            },
            "type": "BinaryExpression"
        },
        "type": "BinaryExpression"
    }
    json_output = parser.ast_as_json()
    assert json.loads(json_output) == expected_json, f"JSON output mismatch: expected {expected_json}, got {json_output}"

def test_empty_expression():
    expression = ""
    parser = ArithmeticExpression(expression)
    ast = parser.parse()
    assert ast is None, f"Expected None for empty expression, got {repr(ast)}"

def test_invalid_expression():
    expression = "3 + * 5"
    parser = ArithmeticExpression(expression)
    with pytest.raises(ValueError, match=r"Unexpected token: Token\(type=MUL, value=\*, position=4\)"):
        parser.parse()

def test_unary_minus():
    expression = "-3"
    parser = ArithmeticExpression(expression)
    ast = parser.parse()

    expected_ast = UnaryExpression(
        operator=Token('MINUS', '-', 0),
        operand=Literal(Decimal('3'))
    )

    assert ast == expected_ast, f"AST mismatch: expected {repr(expected_ast)}, got {repr(ast)}"
