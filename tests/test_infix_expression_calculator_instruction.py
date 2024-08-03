import pytest
import json
from unittest.mock import patch
from compiler.instructions.infix_expression_calculator_instruction import InfixExpressionCalculatorInstruction
from compiler.parser.arithmetic_expression import ArithmeticExpression

@pytest.fixture
def setup_instruction():
    # Example AST structure for the expression "3 + 5 * (10 - -4.5)"
    ast = {
        "left": {"value": 3.0, "type": "Literal"},
        "operator": {"type": "PLUS", "value": "+"},
        "right": {
            "left": {"value": 5.0, "type": "Literal"},
            "operator": {"type": "MUL", "value": "*"},
            "right": {
                "left": {"value": 10.0, "type": "Literal"},
                "operator": {"type": "MINUS", "value": "-"},
                "right": {"value": -4.5, "type": "Literal"}
            }
        },
        "type": "BinaryExpression"
    }
    instruction = InfixExpressionCalculatorInstruction(ast=ast, tokens=None)
    return instruction

@patch.object(InfixExpressionCalculatorInstruction, 'get_random_instruction', return_value="Calculate 3 + 5 * (10 - -4.5) and show the result")
@patch.object(InfixExpressionCalculatorInstruction, 'safe_eval', return_value=75.5)
def test_to_json(mock_safe_eval, mock_get_instruction, setup_instruction):
    json_output = setup_instruction.emit_json()
    expected_result = json.dumps({
        "instruction": "Calculate 3 + 5 * (10 - -4.5) and show the result",
        "expression": "3 + 5 * (10 - -4.5)",
        "tokens": [],  # Tokens are not relevant
        "result": "75.5",
        "explanation": "This explanation details the steps taken to evaluate the expression."
    }, indent=2)
    assert json.loads(json_output) == json.loads(expected_result)

@patch.object(InfixExpressionCalculatorInstruction, 'get_random_instruction', return_value="Calculate 3 + 5 * (10 - -4.5) and show the result")
@patch.object(InfixExpressionCalculatorInstruction, 'safe_eval', return_value=75.5)
def test_to_jsonl(mock_safe_eval, mock_get_instruction, setup_instruction):
    jsonl_output = setup_instruction.emit_jsonl().strip()
    expected_result = json.dumps({
        "instruction": "Calculate 3 + 5 * (10 - -4.5) and show the result",
        "expression": "3 + 5 * (10 - -4.5)",
        "tokens": [],  # Tokens are not relevant
        "result": "75.5",
        "explanation": "This explanation details the steps taken to evaluate the expression."
    })
    assert json.loads(jsonl_output) == json.loads(expected_result)

@patch.object(InfixExpressionCalculatorInstruction, 'get_random_instruction', return_value="Calculate 3 + 5 * (10 - -4.5) and show the result")
@patch.object(InfixExpressionCalculatorInstruction, 'safe_eval', return_value=75.5)
def test_to_qa(mock_safe_eval, mock_get_instruction, setup_instruction):
    qa_output = setup_instruction.emit_qa().strip()
    expected_result = (
        "QUESTION: Calculate 3 + 5 * (10 - -4.5) and show the result\n"
        "ANSWER: 75.5\n"
        "EXPLANATION: This explanation details the steps taken to evaluate the expression."
    )
    assert qa_output == expected_result
