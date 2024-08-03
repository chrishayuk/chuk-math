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
        # move to next token
        self.current_pos += 1

        # check we stil got tokens
        if self.current_pos < len(self.tokens):
            # set the current token
            self.current_token = self.tokens[self.current_pos]
        else:
            # no more tokens
            self.current_token = None

    def parse(self) -> Optional[ASTNode]:
        """Parse the tokens to create an AST."""
        if not self.tokens:
            # no tokens
            return None
        
        # parse the expression
        return self.parse_expression()

    def parse_expression(self, precedence=0) -> Optional[ASTNode]:
        """Parse an expression based on the precedence."""
        # Parse the initial primary expression
        left = self.parse_primary()

        # keep going if we have token, and it's an operator
        while self.current_token and self.current_token.type in {
            TokenType.PLUS, TokenType.MINUS, TokenType.MUL, TokenType.DIV, TokenType.POW
        }:
            # get the precedence
            current_precedence = self.get_operator_precedence(self.current_token.type)

            # check the precedence
            if current_precedence <= precedence:
                break

            # get the operator
            operator = self.current_token

            # next token
            self.advance()

            # parse the right hand side of the expression
            right = self.parse_expression(current_precedence)

            # set the left handside
            left = BinaryExpression(left, operator, right)

        # return the expression
        return left

    def parse_primary(self) -> Optional[ASTNode]:
        token = self.current_token

        if token is None:
            return None

        if token.type == TokenType.NUMBER:
            self.advance()

            # return a literal for the number
            return Literal(Decimal(token.value))
        elif token.type == TokenType.MINUS:
            # Handle unary minus as a UnaryExpression
            self.advance()

            # parse primary
            operand = self.parse_primary()

            # return a unary expression
            return UnaryExpression(operator=token, operand=operand)
        elif token.type == TokenType.LPAREN:
            self.advance()
            expr = self.parse_expression()
            if not (self.current_token and self.current_token.type == TokenType.RPAREN):
                raise SyntaxError("Expected ')'")
            self.advance()
            return expr
        else:
            raise SyntaxError(f"Unexpected token: {token}")

    def get_operator_precedence(self, operator_type: str) -> int:
        """Return the precedence of the operator."""
        precedences = {
            TokenType.PLUS: 5, TokenType.MINUS: 5,
            TokenType.MUL: 6, TokenType.DIV: 6,
            TokenType.POW: 7,
        }

        # return the precedence
        return precedences.get(operator_type, 0)
