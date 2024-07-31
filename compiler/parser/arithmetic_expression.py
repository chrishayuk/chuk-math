import json
from typing import List, Dict, Any
from compiler.lexer.tokenizer import Tokenizer, TokenizationError, Token
from compiler.parser.parser import Parser 

class ArithmeticExpression:
    def __init__(self, expression: str):
        self.expression = expression.strip()

    def tokenize(self) -> List[Dict[str, Any]]:
        """Tokenizes the expression and returns a list of token dictionaries."""
        try:
            tokenizer = Tokenizer(self.expression)
            token_list = tokenizer.tokenize()

            tokens = []
            previous_token = None

            for token in token_list:
                token_dict = {
                    'type': token.type.lower(),
                    'value': token.value,
                    'position': token.position
                }
                tokens.append(token_dict)

                if previous_token and previous_token['type'] == 'operator' and token_dict['type'] == 'operator':
                    raise ValueError(f"Invalid expression: consecutive operators '{previous_token['value']}{token_dict['value']}' at position {token_dict['position']}")

                previous_token = token_dict

            if tokens and tokens[-1]['type'] == 'operator':
                raise ValueError(f"Invalid expression: ends with an operator '{tokens[-1]['value']}'")

            return tokens

        except TokenizationError as error:
            raise ValueError(f"Error parsing expression '{self.expression}': {error}")

    def parse(self) -> Any:
        """Parses the expression and returns the AST."""
        try:
            # Tokenize the expression
            tokens = self.tokenize()
            
            token_objects = [
                Token(type_=token['type'], value=token['value'], position=token['position'])
                for token in tokens
            ]

            # Parse the tokens to create an AST
            parser = Parser(token_objects)
            ast = parser.parse()
            return ast
        except Exception as error:
            raise ValueError(f"Error parsing expression to AST: {error}")

    def parse_as_json(self) -> str:
        """Parses the expression and returns the AST as a JSON string."""
        try:
            ast = self.parse()
            # Assuming AST nodes have a to_dict() method to convert to a dictionary
            return json.dumps(ast.to_dict(), indent=2)
        except Exception as error:
            raise ValueError(f"Error parsing expression to JSON: {error}")

    def parse_tokens_as_json(self) -> str:
        """Tokenizes the expression and returns the tokens as a JSON string."""
        try:
            tokens = self.tokenize()
            return json.dumps({'tokens': tokens}, indent=2)
        except Exception as error:
            raise ValueError(f"Error tokenizing expression to JSON: {error}")
