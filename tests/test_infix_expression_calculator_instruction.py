import pytest
import json
from unittest.mock import patch
from instructions.infix_expression_calculator_instruction import InfixExpressionCalculatorInstruction
from lexer.arithmetic_expression import ArithmeticExpression

@pytest.fixture
def setup_instruction():
    expression = "3 + 5 * (10 - -4.5)"
    arithmetic_expression = ArithmeticExpression(expression)
    json_expression = arithmetic_expression.parse_as_json()
    instruction = InfixExpressionCalculatorInstruction(json_expression, expression)
    return instruction

@patch.object(InfixExpressionCalculatorInstruction, 'get_random_instruction', return_value="Calculate 3 + 5 * (10 - -4.5) and show the result")
def test_create_instruction(mock_get_instruction, setup_instruction):
    instruction = setup_instruction.create_instruction()
    assert "instruction" in instruction
    assert "expression" in instruction
    assert "tokens" in instruction
    assert "result" in instruction
    assert "explanation" in instruction
    assert instruction["result"] == "75.5"

@patch.object(InfixExpressionCalculatorInstruction, 'get_random_instruction', return_value="Calculate 3 + 5 * (10 - -4.5) and show the result")
def test_to_json(mock_get_instruction, setup_instruction):
    json_output = setup_instruction.to_json()
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
        "explanation": "Explanation of the steps taken in solving the expression."
    }, indent=2)
    assert json.loads(json_output) == json.loads(expected_result)

@patch.object(InfixExpressionCalculatorInstruction, 'get_random_instruction', return_value="Calculate 3 + 5 * (10 - -4.5) and show the result")
def test_to_jsonl(mock_get_instruction, setup_instruction):
    jsonl_output = setup_instruction.to_jsonl().strip()
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
        "explanation": "Explanation of the steps taken in solving the expression."
    })
    assert json.loads(jsonl_output) == json.loads(expected_result)

@patch.object(InfixExpressionCalculatorInstruction, 'get_random_instruction', return_value="Calculate 3 + 5 * (10 - -4.5) and show the result")
def test_to_llama2(mock_get_instruction, setup_instruction):
    llama2_output = setup_instruction.to_llama2().strip()
    expected_result = "<s>[INST]Calculate 3 + 5 * (10 - -4.5) and show the result[/INST] 75.5</s>"
    assert llama2_output == expected_result

@patch.object(InfixExpressionCalculatorInstruction, 'get_random_instruction', return_value="Calculate 3 + 5 * (10 - -4.5) and show the result")
def test_to_qa(mock_get_instruction, setup_instruction):
    qa_output = setup_instruction.to_qa().strip()
    expected_result = (
        "QUESTION: Calculate 3 + 5 * (10 - -4.5) and show the result\n"
        "ANSWER: 75.5\n"
        "EXPLANATION: Explanation of the steps taken in solving the expression."
    )
    assert qa_output == expected_result
