"""Tests for AST expression classes."""

from decimal import Decimal
from chuk_math_gym.compiler.ast.ast_node import ASTNode
from chuk_math_gym.compiler.ast.expressions.expression import Expression
from chuk_math_gym.compiler.ast.expressions.literal_expression import Literal
from chuk_math_gym.compiler.ast.expressions.unary_expression import UnaryExpression
from chuk_math_gym.compiler.ast.expressions.binary_expression import BinaryExpression
from chuk_math_gym.compiler.lexer.token_type import TokenType
from chuk_math_gym.compiler.lexer.token import Token


class TestASTNode:
    """Tests for ASTNode base class."""

    def test_repr(self):
        """Test __repr__ method."""
        node = ASTNode()
        repr_str = repr(node)
        assert "ASTNode" in repr_str


class TestExpression:
    """Tests for Expression class."""

    def test_repr(self):
        """Test __repr__ method."""
        expr = Expression()
        repr_str = repr(expr)
        assert "Expression" in repr_str


class TestLiteral:
    """Tests for Literal expression class."""

    def test_create_integer_literal(self):
        """Test creating a literal with an integer value."""
        lit = Literal(42)
        assert lit.value == Decimal(42)

    def test_create_float_literal(self):
        """Test creating a literal with a float value."""
        lit = Literal("3.14")  # Use string to avoid float precision issues
        assert lit.value == Decimal("3.14")

    def test_create_string_literal(self):
        """Test creating a literal with a string number."""
        lit = Literal("123")
        assert lit.value == Decimal(123)

    def test_create_invalid_literal(self):
        """Test creating a literal with invalid value falls back."""
        lit = Literal("invalid")
        assert lit.value == "invalid"

    def test_str(self):
        """Test string representation."""
        lit = Literal(42)
        assert str(lit) == "42"

    def test_to_dict_integer(self):
        """Test to_dict for integer value."""
        lit = Literal(42)
        d = lit.to_dict()
        assert d["type"] == "LiteralExpression"
        assert d["value"] == 42
        assert isinstance(d["value"], int)

    def test_to_dict_float(self):
        """Test to_dict for float value."""
        lit = Literal(3.14)
        d = lit.to_dict()
        assert d["type"] == "LiteralExpression"
        assert d["value"] == 3.14
        assert isinstance(d["value"], float)

    def test_to_dict_non_numeric(self):
        """Test to_dict for non-numeric value."""
        lit = Literal("x")
        d = lit.to_dict()
        assert d["type"] == "LiteralExpression"
        assert d["value"] == "x"

    def test_equality_same_value(self):
        """Test equality between literals with same value."""
        lit1 = Literal(42)
        lit2 = Literal(42)
        assert lit1 == lit2

    def test_equality_different_value(self):
        """Test equality between literals with different values."""
        lit1 = Literal(42)
        lit2 = Literal(43)
        assert lit1 != lit2

    def test_equality_non_literal(self):
        """Test equality with non-Literal object."""
        lit = Literal(42)
        assert lit != 42
        assert lit != "42"


class TestUnaryExpression:
    """Tests for UnaryExpression class."""

    def test_create_unary_expression(self):
        """Test creating a unary expression."""
        operand = Literal(5)
        operator = Token(TokenType.MINUS, "-", 0)
        unary = UnaryExpression(operator, operand)

        assert unary.operator == operator
        assert unary.operand == operand

    def test_repr(self):
        """Test __repr__ method."""
        operand = Literal(5)
        operator = Token(TokenType.MINUS, "-", 0)
        unary = UnaryExpression(operator, operand)

        repr_str = repr(unary)
        assert "UnaryExpression" in repr_str
        assert "operator" in repr_str

    def test_to_dict(self):
        """Test to_dict method."""
        operand = Literal(5)
        operator = Token(TokenType.MINUS, "-", 0)
        unary = UnaryExpression(operator, operand)

        d = unary.to_dict()
        assert d["type"] == "UnaryExpression"
        assert d["operator"] == "-"
        assert d["operand"]["type"] == "LiteralExpression"

    def test_to_dict_string_operator(self):
        """Test to_dict with operator without value attribute."""
        operand = Literal(5)
        unary = UnaryExpression("-", operand)

        d = unary.to_dict()
        assert d["type"] == "UnaryExpression"
        assert d["operator"] == "-"

    def test_equality_same(self):
        """Test equality between same unary expressions."""
        operand1 = Literal(5)
        operand2 = Literal(5)
        operator1 = Token(TokenType.MINUS, "-", 0)
        operator2 = Token(TokenType.MINUS, "-", 0)
        unary1 = UnaryExpression(operator1, operand1)
        unary2 = UnaryExpression(operator2, operand2)

        assert unary1 == unary2

    def test_equality_different_operator(self):
        """Test equality with different operators."""
        operand1 = Literal(5)
        operand2 = Literal(5)
        operator1 = Token(TokenType.MINUS, "-", 0)
        operator2 = Token(TokenType.PLUS, "+", 0)
        unary1 = UnaryExpression(operator1, operand1)
        unary2 = UnaryExpression(operator2, operand2)

        assert unary1 != unary2

    def test_equality_different_operand(self):
        """Test equality with different operands."""
        operand1 = Literal(5)
        operand2 = Literal(10)
        operator = Token(TokenType.MINUS, "-", 0)
        unary1 = UnaryExpression(operator, operand1)
        unary2 = UnaryExpression(operator, operand2)

        assert unary1 != unary2

    def test_equality_non_unary(self):
        """Test equality with non-UnaryExpression object."""
        operand = Literal(5)
        operator = Token(TokenType.MINUS, "-", 0)
        unary = UnaryExpression(operator, operand)

        assert unary != operand
        assert unary != "-5"


class TestBinaryExpression:
    """Tests for BinaryExpression class."""

    def test_create_binary_expression(self):
        """Test creating a binary expression."""
        left = Literal(3)
        right = Literal(5)
        operator = Token(TokenType.PLUS, "+", 0)
        binary = BinaryExpression(left, operator, right)

        assert binary.left == left
        assert binary.operator == operator
        assert binary.right == right

    def test_str(self):
        """Test string representation."""
        left = Literal(3)
        right = Literal(5)
        operator = Token(TokenType.PLUS, "+", 0)
        binary = BinaryExpression(left, operator, right)

        assert str(binary) == "3 + 5"

    def test_to_dict(self):
        """Test to_dict method."""
        left = Literal(3)
        right = Literal(5)
        operator = Token(TokenType.PLUS, "+", 0)
        binary = BinaryExpression(left, operator, right)

        d = binary.to_dict()
        assert d["type"] == "BinaryExpression"
        assert d["operator"] == "+"
        assert d["left"]["type"] == "LiteralExpression"
        assert d["right"]["type"] == "LiteralExpression"

    def test_to_dict_string_operator(self):
        """Test to_dict with operator without value attribute."""
        left = Literal(3)
        right = Literal(5)
        binary = BinaryExpression(left, "+", right)

        d = binary.to_dict()
        assert d["operator"] == "+"

    def test_equality_same(self):
        """Test equality between same binary expressions."""
        left1, right1 = Literal(3), Literal(5)
        left2, right2 = Literal(3), Literal(5)
        op1 = Token(TokenType.PLUS, "+", 0)
        op2 = Token(TokenType.PLUS, "+", 0)
        binary1 = BinaryExpression(left1, op1, right1)
        binary2 = BinaryExpression(left2, op2, right2)

        assert binary1 == binary2

    def test_equality_different(self):
        """Test equality with different expressions."""
        left = Literal(3)
        right = Literal(5)
        op1 = Token(TokenType.PLUS, "+", 0)
        op2 = Token(TokenType.MINUS, "-", 0)
        binary1 = BinaryExpression(left, op1, right)
        binary2 = BinaryExpression(left, op2, right)

        assert binary1 != binary2

    def test_equality_non_binary(self):
        """Test equality with non-BinaryExpression object."""
        left = Literal(3)
        right = Literal(5)
        operator = Token(TokenType.PLUS, "+", 0)
        binary = BinaryExpression(left, operator, right)

        assert binary != left
        assert binary != "3 + 5"
