"""Tests for the InstructionEmitter class."""

from typing import Any
from decimal import Decimal
from unittest.mock import MagicMock

from chuk_math_gym.compiler.instructions.instruction_emitter import (
    InstructionEmitter,
)


class ConcreteInstructionEmitter(InstructionEmitter):
    """Concrete implementation for testing."""

    def get_random_instruction(self, use_llm: bool = False) -> str:
        return f"Calculate: {self.expression}"

    def generate_placeholder_explanation(self) -> str:
        return "Step 1: Evaluate the expression"

    def safe_eval(self, expression: str) -> Any:
        try:
            return Decimal(str(eval(expression)))
        except Exception:
            raise ValueError(f"Cannot evaluate: {expression}")


class TestInstructionEmitterInit:
    """Test InstructionEmitter initialization."""

    def test_init_no_llm(self):
        """Test initialization without LLM."""
        emitter = ConcreteInstructionEmitter()
        assert emitter.ast is None
        assert emitter.tokens == []
        assert emitter.llm is None

    def test_init_with_ast(self):
        """Test initialization with AST."""
        ast = {"type": "Literal", "value": 42}
        emitter = ConcreteInstructionEmitter(ast=ast)
        assert emitter.ast == ast

    def test_init_with_tokens(self):
        """Test initialization with tokens."""
        tokens = [{"type": "NUMBER", "value": 42}]
        emitter = ConcreteInstructionEmitter(tokens=tokens)
        assert emitter.tokens == tokens


class TestExtractExpressionFromAST:
    """Test extract_expression_from_ast method."""

    def test_extract_literal(self):
        """Test extracting literal expression."""
        ast = {"type": "Literal", "value": 42}
        emitter = ConcreteInstructionEmitter(ast=ast)
        result = emitter.extract_expression_from_ast(ast)
        assert result == "42"

    def test_extract_float_literal(self):
        """Test extracting float literal (whole number)."""
        ast = {"type": "Literal", "value": 42.0}
        emitter = ConcreteInstructionEmitter(ast=ast)
        result = emitter.extract_expression_from_ast(ast)
        assert result == "42"

    def test_extract_binary_expression(self):
        """Test extracting binary expression."""
        ast = {
            "type": "BinaryExpression",
            "operator": {"value": "+"},
            "left": {"type": "Literal", "value": 3},
            "right": {"type": "Literal", "value": 5},
        }
        emitter = ConcreteInstructionEmitter(ast=ast)
        result = emitter.extract_expression_from_ast(ast)
        assert result == "3 + 5"

    def test_extract_unary_expression(self):
        """Test extracting unary expression."""
        ast = {
            "type": "UnaryExpression",
            "operator": {"value": "-"},
            "operand": {"type": "Literal", "value": 5},
        }
        emitter = ConcreteInstructionEmitter(ast=ast)
        result = emitter.extract_expression_from_ast(ast)
        assert result == "-5"

    def test_extract_nested_expression_with_parens(self):
        """Test extracting nested expression that needs parentheses."""
        # (3 + 5) * 2
        ast = {
            "type": "BinaryExpression",
            "operator": {"value": "*"},
            "left": {
                "type": "BinaryExpression",
                "operator": {"value": "+"},
                "left": {"type": "Literal", "value": 3},
                "right": {"type": "Literal", "value": 5},
            },
            "right": {"type": "Literal", "value": 2},
        }
        emitter = ConcreteInstructionEmitter(ast=ast)
        result = emitter.extract_expression_from_ast(ast)
        assert result == "(3 + 5) * 2"

    def test_extract_none_ast(self):
        """Test extracting from None AST."""
        emitter = ConcreteInstructionEmitter()
        result = emitter.extract_expression_from_ast(None)
        assert result == ""

    def test_extract_invalid_ast(self):
        """Test extracting from invalid AST (not dict)."""
        emitter = ConcreteInstructionEmitter()
        result = emitter.extract_expression_from_ast("not a dict")
        assert result == ""


class TestNeedsParentheses:
    """Test _needs_parentheses method."""

    def test_needs_parens_lower_precedence(self):
        """Test that lower precedence operators need parentheses."""
        emitter = ConcreteInstructionEmitter()
        sub_ast = {
            "type": "BinaryExpression",
            "operator": {"value": "+"},
            "left": {"value": 1},
            "right": {"value": 2},
        }
        result = emitter._needs_parentheses(sub_ast, "*")
        assert result is True

    def test_no_parens_higher_precedence(self):
        """Test that higher precedence operators don't need parentheses."""
        emitter = ConcreteInstructionEmitter()
        sub_ast = {
            "type": "BinaryExpression",
            "operator": {"value": "*"},
            "left": {"value": 1},
            "right": {"value": 2},
        }
        result = emitter._needs_parentheses(sub_ast, "+")
        assert result is False

    def test_no_parens_unary(self):
        """Test that unary expressions don't need parentheses."""
        emitter = ConcreteInstructionEmitter()
        sub_ast = {"type": "UnaryExpression", "operator": {"value": "-"}}
        result = emitter._needs_parentheses(sub_ast, "*")
        assert result is False

    def test_no_parens_none(self):
        """Test that None doesn't need parentheses."""
        emitter = ConcreteInstructionEmitter()
        result = emitter._needs_parentheses(None, "*")
        assert result is False

    def test_no_parens_no_operator(self):
        """Test that nodes without operator don't need parentheses."""
        emitter = ConcreteInstructionEmitter()
        sub_ast = {"type": "Literal", "value": 42}
        result = emitter._needs_parentheses(sub_ast, "*")
        assert result is False


class TestEmitInstruction:
    """Test emit_instruction method."""

    def test_emit_instruction_basic(self):
        """Test basic instruction emission."""
        ast = {"type": "Literal", "value": 42}
        emitter = ConcreteInstructionEmitter(ast=ast)
        result = emitter.emit_instruction()

        assert "instruction" in result
        assert "expression" in result
        assert "result" in result
        assert "explanation" in result

    def test_emit_instruction_no_ast(self):
        """Test instruction emission without AST."""
        emitter = ConcreteInstructionEmitter()
        emitter.expression = "3 + 5"
        result = emitter.emit_instruction()

        assert result["expression"] == "3 + 5"


class TestEvaluateExpression:
    """Test evaluate_expression method."""

    def test_evaluate_valid_expression(self):
        """Test evaluating a valid expression."""
        emitter = ConcreteInstructionEmitter()
        emitter.expression = "3 + 5"
        result = emitter.evaluate_expression()
        assert result == "8"

    def test_evaluate_invalid_expression(self):
        """Test evaluating an invalid expression."""
        emitter = ConcreteInstructionEmitter()
        emitter.expression = "invalid"
        result = emitter.evaluate_expression()
        assert "Cannot evaluate" in result


class TestOutputFormats:
    """Test various output format methods."""

    def test_emit_json(self):
        """Test JSON output."""
        ast = {"type": "Literal", "value": 42}
        emitter = ConcreteInstructionEmitter(ast=ast)
        result = emitter.emit_json()

        assert '"instruction"' in result
        assert '"expression"' in result

    def test_emit_jsonl(self):
        """Test JSONL output."""
        ast = {"type": "Literal", "value": 42}
        emitter = ConcreteInstructionEmitter(ast=ast)
        result = emitter.emit_jsonl()

        assert '"instruction"' in result

    def test_emit_qa(self):
        """Test Q&A output."""
        ast = {"type": "Literal", "value": 42}
        emitter = ConcreteInstructionEmitter(ast=ast)
        result = emitter.emit_qa()

        assert "QUESTION:" in result
        assert "ANSWER:" in result


class TestSimplifyTokens:
    """Test simplify_tokens method."""

    def test_simplify_tokens(self):
        """Test token simplification."""

        token = MagicMock()
        token.type = "NUMBER"
        token.value = 42

        emitter = ConcreteInstructionEmitter()
        result = emitter.simplify_tokens([token])

        assert len(result) == 1
        assert result[0]["type"] == "NUMBER"
        assert result[0]["value"] == 42


class TestGetLLMResponse:
    """Test get_llm_response method."""

    def test_get_llm_response_no_llm(self):
        """Test LLM response fallback when no LLM."""
        emitter = ConcreteInstructionEmitter()
        result = emitter.get_llm_response("test input")
        assert result == "test input"
