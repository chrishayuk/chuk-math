import pytest
import json
from unittest.mock import patch
from compiler.instructions.infix_expression_calculator_instruction import InfixExpressionCalculatorInstruction
from compiler.parser.arithmetic_expression import ArithmeticExpression

# Mock Token class with attributes
class MockToken:
    def __init__(self, type, value, position):
        self.type = type
        self.value = value
        self.position = position

@pytest.fixture
def setup_instruction():
    expression = "3 + 5 * (10 - -4.5)"
    arithmetic_expression = ArithmeticExpression(expression)
    # Initialize the instruction with mocked tokens
    tokens = [
        MockToken(type="number", value=3.0, position=0),
        MockToken(type="operator", value="+", position=2),
        MockToken(type="number", value=5.0, position=4),
        MockToken(type="operator", value="*", position=6),
        MockToken(type="parenthesis", value="(", position=8),
        MockToken(type="number", value=10.0, position=9),
        MockToken(type="operator", value="-", position=12),
        MockToken(type="number", value=-4.5, position=14),
        MockToken(type="parenthesis", value=")", position=18)
    ]
    instruction = InfixExpressionCalculatorInstruction(ast=None, tokens=tokens)
    return instruction

@patch.object(InfixExpressionCalculatorInstruction, 'get_random_instruction', return_value="Calculate 3 + 5 * (10 - -4.5) and show the result")
@patch.object(InfixExpressionCalculatorInstruction, 'safe_eval', return_value=75.5)
def test_to_json(mock_safe_eval, mock_get_instruction, setup_instruction):
    json_output = setup_instruction.emit_json()
    expected_result = json.dumps({
        "instruction": "Calculate 3 + 5 * (10 - -4.5) and show the result",
        "expression": "3 + 5 * (10 - -4.5)",
        "tokens": [
            {"type": "number", "value": 3.0, "position": 0},
            {"type": "operator", "value": "+", "position": 2},
            {"type": "number", "value": 5.0, "position": 4},
            {"type": "operator", "value": "*", "position": 6},
            {"type": "parenthesis", "value": "(", "position": 8},
            {"type": "number", "value": 10.0, "position": 9},
            {"type": "operator", "value": "-", "position": 12},
            {"type": "number", "value": -4.5, "position": 14},
            {"type": "parenthesis", "value": ")", "position": 18}
        ],
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
        "tokens": [
            {"type": "number", "value": 3.0, "position": 0},
            {"type": "operator", "value": "+", "position": 2},
            {"type": "number", "value": 5.0, "position": 4},
            {"type": "operator", "value": "*", "position": 6},
            {"type": "parenthesis", "value": "(", "position": 8},
            {"type": "number", "value": 10.0, "position": 9},
            {"type": "operator", "value": "-", "position": 12},
            {"type": "number", "value": -4.5, "position": 14},
            {"type": "parenthesis", "value": ")", "position": 18}
        ],
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
