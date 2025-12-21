import pytest
import json
from unittest.mock import patch
from chuk_math_gym.compiler.instructions.infix_expression_calculator_instruction import InfixExpressionCalculatorInstruction

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
    return InfixExpressionCalculatorInstruction(ast=ast, tokens=[])

@patch.object(InfixExpressionCalculatorInstruction, 'get_random_instruction', return_value="Calculate 3 + 5 * (10 - -4.5) and show the result")
@patch.object(InfixExpressionCalculatorInstruction, 'safe_eval', return_value=75.5)
def test_to_json(mock_safe_eval, mock_get_instruction, setup_instruction):
    setup_instruction.expression = "3 + 5 * (10 - -4.5)"
    json_output = setup_instruction.emit_json()

    actual_output = json.loads(json_output)  # Convert JSON string to dictionary

    # Ensure that the essential fields are correct
    assert actual_output["expression"] == "3 + 5 * (10 - -4.5)"
    assert actual_output["instruction"] == "Calculate 3 + 5 * (10 - -4.5) and show the result"
    assert actual_output["result"] == "75.5"
    # Explanation now contains verifier XML format with step-by-step breakdown
    assert "<verifier_answer>" in actual_output["explanation"]
    assert "<final_result>" in actual_output["explanation"]
    assert "</answer>" in actual_output["explanation"]

@patch.object(InfixExpressionCalculatorInstruction, 'get_random_instruction', return_value="Calculate 3 + 5 * (10 - -4.5) and show the result")
@patch.object(InfixExpressionCalculatorInstruction, 'safe_eval', return_value=75.5)
def test_to_jsonl(mock_safe_eval, mock_get_instruction, setup_instruction):
    setup_instruction.expression = "3 + 5 * (10 - -4.5)"
    jsonl_output = setup_instruction.emit_jsonl().strip()

    actual_output = json.loads(jsonl_output)  # Convert JSON string to dictionary

    # Ensure that the essential fields are correct
    assert actual_output["expression"] == "3 + 5 * (10 - -4.5)"
    assert actual_output["instruction"] == "Calculate 3 + 5 * (10 - -4.5) and show the result"
    assert actual_output["result"] == "75.5"
    # Explanation now contains verifier XML format with step-by-step breakdown
    assert "<verifier_answer>" in actual_output["explanation"]
    assert "<final_result>" in actual_output["explanation"]
    assert "</answer>" in actual_output["explanation"]

@patch.object(InfixExpressionCalculatorInstruction, 'get_random_instruction', return_value="Calculate 3 + 5 * (10 - -4.5) and show the result")
@patch.object(InfixExpressionCalculatorInstruction, 'safe_eval', return_value=75.5)
def test_to_qa(mock_safe_eval, mock_get_instruction, setup_instruction):
    setup_instruction.expression = "3 + 5 * (10 - -4.5)"
    qa_output = setup_instruction.emit_qa().strip()

    # Check the structure of QA output
    assert qa_output.startswith("QUESTION: Calculate 3 + 5 * (10 - -4.5) and show the result")
    assert "ANSWER: 75.5" in qa_output
    assert "EXPLANATION:" in qa_output
    # Explanation now contains verifier XML format
    assert "<verifier_answer>" in qa_output
    assert "</answer>" in qa_output
