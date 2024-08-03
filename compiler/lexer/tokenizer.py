import re
from typing import List
from compiler.lexer.token_type import TokenType  
from compiler.lexer.token import Token

class TokenizationError(Exception):
    pass

class Tokenizer:
    def __init__(self, input_string: str):
        self.input_string = input_string
        self.current_pos = 0
        self.length = len(input_string)
        self.tokens = []  # This list will store tokens as they are created

    def tokenize(self) -> List[Token]:
        # loop to the end
        while self.current_pos < self.length:
            # get next token
            token = self.get_next_token()

            # check we got a token
            if token:
                # we got a tokem, so add it
                self.tokens.append(token)
            else:
                # skip whitespace
                self.skip_whitespace()

                # check if we can keep going
                if self.current_pos < self.length:
                    # get the next next character
                    char = self.input_string[self.current_pos]

                    # unexpected character
                    raise TokenizationError(f"Unexpected character: {char} at position {self.current_pos}")
        
        # return tokens
        return self.tokens

    def get_next_token(self) -> Token:
        # skip whitespace
        self.skip_whitespace()

        # check if we're at the end
        if self.current_pos >= self.length:
            return None
        
        # types of tokens
        token_methods = [
            self.get_number,
            self.get_operator,
            self.get_punctuation,
            self.get_identifier_or_function,
        ]

        # loop through the methods
        for method in token_methods:
            # check the type of token method
            token = method()

            # check we got a token
            if token:
                # return the token
                return token
            
        # no token
        return None

    def get_number(self) -> Token:
        # check for a number using regex
        number_match = re.match(r'\d+(\.\d*)?', self.input_string[self.current_pos:])

        # check for a match
        if number_match:
            # get the number
            number_str = number_match.group(0)
            self.current_pos += len(number_str)

            try:
                # get the value
                value = float(number_str)

                # return the token
                return Token(TokenType.NUMBER, value, self.current_pos - len(number_str))
            except ValueError:
                raise TokenizationError(f"Invalid number literal: {number_str}")
        return None

    def get_operator(self) -> Token:
        # operator list
        operators = {
            '+': TokenType.PLUS,
            '-': TokenType.MINUS,
            '*': TokenType.MUL,
            '/': TokenType.DIV,
            '^': TokenType.POW,
            '=': TokenType.EQ,
            '==': TokenType.EQ,
            '!=': TokenType.NE,
            '<>': TokenType.NE,
            '<=': TokenType.LE,
            '<': TokenType.LT,
            '>=': TokenType.GE,
            '>': TokenType.GT,
            '&&': TokenType.AND,
            '||': TokenType.OR,
            '!': TokenType.NOT
        }

        # loop through the operators
        for op, token_type in sorted(operators.items(), key=lambda x: -len(x[0])):
            # we have an operator
            if self.input_string.startswith(op, self.current_pos):
                # move the position along
                self.current_pos += len(op)

                # return the token
                return Token(token_type, op, self.current_pos - len(op))
            
        # no operators
        return None


    def get_punctuation(self) -> Token:
        # check for punctuation
        punctuations = {
            ',': TokenType.COMMA,
            ':': TokenType.COLON,
            ';': TokenType.SEMI,
            '(': TokenType.LPAREN,
            ')': TokenType.RPAREN,
            '$': TokenType.DOLLAR,
            '%': TokenType.PERCENT
        }

        # check if we have puncatuation
        if self.input_string[self.current_pos] in punctuations:
            # set the value
            value = self.input_string[self.current_pos]

            # move position
            self.current_pos += 1

            # return the punctuation
            return Token(punctuations[value], value, self.current_pos - 1)
        
        # no punctuation
        return None

    def get_identifier_or_function(self) -> Token:
        # check for an identifier or function using regex
        identifier_match = re.match(r'[A-Za-z_][A-Za-z0-9_]*', self.input_string[self.current_pos:])

        # check for a match
        if identifier_match:
            # get the identifier
            identifier = identifier_match.group(0)
            self.current_pos += len(identifier)

            # Look ahead to see if the next character is an opening parenthesis
            if self.current_pos < self.length and self.input_string[self.current_pos] == '(':
                # return the functiontoken
                return Token(TokenType.FUNCTION, identifier, self.current_pos - len(identifier))
            
            # return the identifier token
            return Token(TokenType.IDENTIFIER, identifier, self.current_pos - len(identifier))
        
        # no tokens
        return None

    def skip_whitespace(self):
        # skip past whitespace
        while self.current_pos < self.length and self.input_string[self.current_pos].isspace():
            self.current_pos += 1
