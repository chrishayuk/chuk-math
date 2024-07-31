from decimal import Decimal
from typing import List, Optional
from compiler.ast.ast_node import ASTNode
from compiler.ast.expressions.binary_expression import BinaryExpression
from compiler.ast.expressions.literal_expression import Literal
from compiler.ast.expressions.unary_expression import UnaryExpression
from compiler.lexer.token_type import TokenType
from compiler.lexer.tokenizer import Token

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current_pos = 0
        self.current_token = self.tokens[self.current_pos] if self.tokens else None

    def advance(self):
        """Advance to the next token in the stream."""
        self.current_pos += 1
        if self.current_pos < len(self.tokens):
            self.current_token = self.tokens[self.current_pos]
        else:
            self.current_token = None

    def parse(self) -> Optional[ASTNode]:
        """Parse the tokens to create an AST."""
        if not self.tokens:
            return None  # or raise an appropriate exception

        return self.parse_expression()

    def parse_expression(self, precedence=0) -> Optional[ASTNode]:
        """Parse an expression based on the precedence."""
        # Parse the initial primary expression
        left = self.parse_primary()

        while self.current_token and self.current_token.type == 'OPERATOR':
            current_precedence = self.get_operator_precedence(self.current_token.value)
            if current_precedence <= precedence:
                break

            operator = self.current_token
            self.advance()
            right = self.parse_expression(current_precedence)
            left = BinaryExpression(left, operator, right)

        return left


    def parse_primary(self) -> ASTNode:
        """Parse primary expressions, such as literals, unary expressions, and parenthesized expressions."""
        token = self.current_token

        if token is None:
            return None  # Handle empty input gracefully

        if token.type == 'NUMBER':
            self.advance()
            return Literal(token.value)
        elif token.type == 'OPERATOR' and token.value == '-':
            # Handle unary minus
            self.advance()
            operand = self.parse_primary()
            return UnaryExpression(operator=token, operand=operand)
        elif token.type == 'PARENTHESIS' and token.value == '(':
            self.advance()
            expr = self.parse_expression()
            if not (self.current_token and self.current_token.type == 'PARENTHESIS' and self.current_token.value == ')'):
                raise SyntaxError("Expected ')'")
            self.advance()
            return expr
        else:
            raise SyntaxError(f"Unexpected token: {token}")








    def get_operator_precedence(self, operator_value: str) -> int:
        """Return the precedence of the operator."""
        precedences = {
            '+': 5, '-': 5,
            '*': 6, '/': 6,
            '^': 7,
        }
        return precedences.get(operator_value, 0)
