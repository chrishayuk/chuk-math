# tokenizer.py
import re
from typing import List
from lexer.token_type import TokenType
from lexer.token import Token

class TokenizationError(Exception):
    pass

class Tokenizer:
    def __init__(self, input_string: str):
        self.input_string = input_string
        self.current_pos = 0
        self.length = len(input_string)

    def tokenize(self) -> List[Token]:
        tokens = []
        while self.current_pos < self.length:
            token = self.get_next_token()
            if token:
                tokens.append(token)
            else:
                self.skip_whitespace()
                if self.current_pos < self.length:
                    char = self.input_string[self.current_pos]
                    raise TokenizationError(f"Unexpected character: {char} at position {self.current_pos}")
        return tokens

    def get_next_token(self) -> Token:
        self.skip_whitespace()
        if self.current_pos >= self.length:
            return None

        token_methods = [
            self.get_number,
            self.get_operator,
            self.get_parenthesis,
            self.get_identifier_or_function,
        ]

        for method in token_methods:
            token = method()
            if token:
                return token
        return None

    def get_number(self) -> Token:
        number_match = re.match(r'-?\d+(\.\d*)?', self.input_string[self.current_pos:])
        if number_match:
            number_str = number_match.group(0)
            self.current_pos += len(number_str)
            try:
                value = float(number_str)
                return Token(TokenType.NUMBER, value, self.current_pos - len(number_str))
            except ValueError:
                raise TokenizationError(f"Invalid number literal: {number_str}")
        return None

    def get_operator(self) -> Token:
        operators = {'+', '-', '*', '/'}
        if self.input_string[self.current_pos] in operators:
            value = self.input_string[self.current_pos]
            self.current_pos += 1
            return Token(TokenType.OPERATOR, value, self.current_pos - 1)
        return None

    def get_parenthesis(self) -> Token:
        if self.input_string[self.current_pos] in '()':
            value = self.input_string[self.current_pos]
            self.current_pos += 1
            return Token(TokenType.PARENTHESIS, value, self.current_pos - 1)
        return None

    def get_identifier_or_function(self) -> Token:
        identifier_match = re.match(r'[A-Za-z_][A-Za-z0-9_]*', self.input_string[self.current_pos:])
        if identifier_match:
            identifier = identifier_match.group(0)
            self.current_pos += len(identifier)
            # Check if the identifier is followed by an open parenthesis, indicating a function call
            if self.current_pos < self.length and self.input_string[self.current_pos] == '(':
                return Token(TokenType.FUNCTION, identifier, self.current_pos - len(identifier))
            return Token(TokenType.IDENTIFIER, identifier, self.current_pos - len(identifier))
        return None

    def skip_whitespace(self):
        while self.current_pos < self.length and self.input_string[self.current_pos].isspace():
            self.current_pos += 1

