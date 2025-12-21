"""Tests for the MATHProblemInstruction class."""

import pytest
from decimal import Decimal
from unittest.mock import patch, MagicMock

from chuk_math_gym.compiler.instructions.math_problem_instruction import (
    MATHProblemInstruction,
)


@pytest.fixture
def simple_ast():
    """Simple AST for 3 + 5."""
    return {
        "left": {"value": 3.0, "type": "Literal"},
        "operator": {"type": "PLUS", "value": "+"},
        "right": {"value": 5.0, "type": "Literal"},
        "type": "BinaryExpression",
    }


@pytest.fixture
def instruction(simple_ast):
    """Create a MATHProblemInstruction instance."""
    return MATHProblemInstruction(ast=simple_ast, tokens=[])


class TestMATHProblemInstructionInit:
    """Test MATHProblemInstruction initialization."""

    def test_init_with_dict(self, simple_ast):
        """Test initialization with dict AST."""
        inst = MATHProblemInstruction(ast=simple_ast)
        assert inst.ast == simple_ast
        assert inst.tokens == []
        assert inst.llm is None

    def test_init_with_json_string(self, simple_ast):
        """Test initialization with JSON string AST."""
        import json

        ast_str = json.dumps(simple_ast)
        inst = MATHProblemInstruction(ast=ast_str)
        assert inst.ast == simple_ast

    def test_init_with_tokens(self, simple_ast):
        """Test initialization with tokens."""
        tokens = [{"type": "NUMBER", "value": 3}]
        inst = MATHProblemInstruction(ast=simple_ast, tokens=tokens)
        assert inst.tokens == tokens

    def test_init_with_llm(self, simple_ast):
        """Test initialization with LLM name."""
        inst = MATHProblemInstruction(ast=simple_ast, llm="test-model")
        assert inst.llm is not None


class TestGetRandomInstruction:
    """Test get_random_instruction method."""

    def test_get_random_instruction_no_llm(self, instruction):
        """Test getting instruction without LLM."""
        instruction.expression = "3 + 5"
        result = instruction.get_random_instruction(use_llm=False)

        assert "3 + 5" in result
        assert "Solve for the value" in result

    def test_get_random_instruction_with_llm_disabled(self, instruction):
        """Test getting instruction with LLM disabled."""
        instruction.expression = "10 - 2"
        result = instruction.get_random_instruction(use_llm=False)

        assert "10 - 2" in result

    def test_get_random_instruction_llm_returns_error(self, simple_ast):
        """Test behavior when LLM returns an error."""
        inst = MATHProblemInstruction(ast=simple_ast, llm="test-model")
        inst.expression = "3 + 5"

        with patch.object(inst, "get_instruction_from_llm", return_value="Error: something failed"):
            result = inst.get_random_instruction(use_llm=True)
            # Should fall back to default instruction
            assert "Solve for the value" in result


class TestGetInstructionFromLLM:
    """Test get_instruction_from_llm method."""

    def test_no_llm_configured(self, instruction):
        """Test error when no LLM is configured."""
        result = instruction.get_instruction_from_llm("test question")
        assert "Error: No LLM configured" in result

    def test_llm_exception_handling(self, simple_ast):
        """Test exception handling in LLM call."""
        inst = MATHProblemInstruction(ast=simple_ast, llm="test-model")
        inst.expression = "3 + 5"

        # Mock the chain to raise an exception
        with patch.object(inst, "llm") as mock_llm:
            mock_llm.__or__ = MagicMock(side_effect=Exception("LLM error"))
            result = inst.get_instruction_from_llm("test")
            assert "Error generating instruction from LLM" in result


class TestSafeEval:
    """Test safe_eval method."""

    def test_simple_addition(self, instruction):
        """Test evaluating simple addition."""
        result = instruction.safe_eval("3 + 5")
        assert result == Decimal("8")

    def test_simple_subtraction(self, instruction):
        """Test evaluating simple subtraction."""
        result = instruction.safe_eval("10 - 3")
        assert result == Decimal("7")

    def test_multiplication(self, instruction):
        """Test evaluating multiplication."""
        result = instruction.safe_eval("4 * 5")
        assert result == Decimal("20")

    def test_division(self, instruction):
        """Test evaluating division."""
        result = instruction.safe_eval("10 / 2")
        assert result == Decimal("5")

    def test_complex_expression(self, instruction):
        """Test evaluating complex expression."""
        result = instruction.safe_eval("(2 + 3) * 4")
        assert result == Decimal("20")

    def test_negative_numbers(self, instruction):
        """Test evaluating with negative numbers."""
        result = instruction.safe_eval("-5 + 3")
        assert result == Decimal("-2")

    def test_decimal_result(self, instruction):
        """Test evaluating expression with decimal result."""
        result = instruction.safe_eval("5 / 2")
        assert result == Decimal("2.5")

    def test_invalid_expression(self, instruction):
        """Test evaluating invalid expression."""
        with pytest.raises(ValueError):
            instruction.safe_eval("invalid expression")

    def test_none_result(self, instruction):
        """Test when sympify returns None-like result."""
        with patch("chuk_math_gym.compiler.instructions.math_problem_instruction.sympify") as mock:
            mock.return_value = None
            with pytest.raises(ValueError):
                instruction.safe_eval("3 + 5")


class TestGenerateExplanation:
    """Test explanation generation methods."""

    def test_generate_explanation(self, instruction):
        """Test generate_explanation returns string."""
        result = instruction.generate_explanation()
        assert isinstance(result, str)
        assert "explanation" in result.lower()

    def test_generate_placeholder_explanation(self, instruction):
        """Test generate_placeholder_explanation returns explanation."""
        result = instruction.generate_placeholder_explanation()
        assert isinstance(result, str)
        assert result == instruction.generate_explanation()


class TestEmitInstruction:
    """Test emit_instruction method."""

    def test_emit_instruction_structure(self, instruction):
        """Test that emit_instruction returns proper structure."""
        instruction.expression = "3 + 5"
        with patch.object(instruction, "safe_eval", return_value=Decimal("8")):
            result = instruction.emit_instruction()

        assert isinstance(result, dict)
        assert "instruction" in result
        assert "expression" in result
        assert "result" in result
        assert "explanation" in result

    def test_emit_json(self, instruction):
        """Test emit_json method."""
        instruction.expression = "3 + 5"
        with patch.object(instruction, "safe_eval", return_value=Decimal("8")):
            result = instruction.emit_json()

        assert isinstance(result, str)
        import json

        parsed = json.loads(result)
        assert "expression" in parsed

    def test_emit_qa(self, instruction):
        """Test emit_qa method."""
        instruction.expression = "3 + 5"
        with patch.object(instruction, "safe_eval", return_value=Decimal("8")):
            result = instruction.emit_qa()

        assert "QUESTION:" in result
        assert "ANSWER:" in result
