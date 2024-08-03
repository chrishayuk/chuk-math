from compiler.lexer.tokenizer import Tokenizer
from compiler.parser.parser import Parser
from compiler.ast.expressions.literal_expression import Literal
from compiler.ast.expressions.binary_expression import BinaryExpression
from compiler.ast.expressions.unary_expression import UnaryExpression
from compiler.lexer.token_type import TokenType
from compiler.lexer.tokenizer import Token

# Helper function to generate tokens from an expression string
def tokenize(expression):
    tokenizer = Tokenizer(expression)
    return tokenizer.tokenize()

# Helper function to parse tokens into an AST
def parse_tokens(expression):
    tokens = tokenize(expression)
    parser = Parser(tokens)
    return parser.parse()

def test_literal_expression():
    expression = "3"
    ast = parse_tokens(expression)
    assert isinstance(ast, Literal)
    assert ast.value == 3

def test_simple_addition():
    expression = "3 + 5"
    ast = parse_tokens(expression)
    assert isinstance(ast, BinaryExpression)
    assert ast.operator.value == '+'
    assert isinstance(ast.left, Literal)
    assert ast.left.value == 3
    assert isinstance(ast.right, Literal)
    assert ast.right.value == 5

def test_operator_precedence():
    expression = "3 + 5 * 2"
    ast = parse_tokens(expression)
    assert isinstance(ast, BinaryExpression)
    assert ast.operator.value == '+'
    assert isinstance(ast.left, Literal)
    assert ast.left.value == 3
    assert isinstance(ast.right, BinaryExpression)
    assert ast.right.operator.value == '*'
    assert isinstance(ast.right.left, Literal)
    assert ast.right.left.value == 5
    assert isinstance(ast.right.right, Literal)
    assert ast.right.right.value == 2

def test_parentheses():
    expression = "(3 + 5) * 2"
    ast = parse_tokens(expression)
    assert isinstance(ast, BinaryExpression)
    assert ast.operator.value == '*'
    assert isinstance(ast.left, BinaryExpression)
    assert ast.left.operator.value == '+'
    assert isinstance(ast.left.left, Literal)
    assert ast.left.left.value == 3
    assert isinstance(ast.left.right, Literal)
    assert ast.left.right.value == 5
    assert isinstance(ast.right, Literal)
    assert ast.right.value == 2

def test_unary_minus():
    expression = "-3"
    tokens = tokenize(expression)  # Assuming tokenize is the function that uses the tokenizer
    print(tokens)  # Debugging line to check the generated tokens
    ast = parse_tokens(expression)
    assert isinstance(ast, UnaryExpression)

def test_complex_expression():
    expression = "3 + 5 * (10 - 4)"
    ast = parse_tokens(expression)
    assert isinstance(ast, BinaryExpression)
    assert ast.operator.value == '+'
    assert isinstance(ast.left, Literal)
    assert ast.left.value == 3
    assert isinstance(ast.right, BinaryExpression)
    assert ast.right.operator.value == '*'
    assert isinstance(ast.right.left, Literal)
    assert ast.right.left.value == 5
    assert isinstance(ast.right.right, BinaryExpression)
    assert ast.right.right.operator.value == '-'
    assert isinstance(ast.right.right.left, Literal)
    assert ast.right.right.left.value == 10
    assert isinstance(ast.right.right.right, Literal)
    assert ast.right.right.right.value == 4

