from compiler.lexer.tokenizer import Tokenizer, TokenizationError
from compiler.parser.parser import Parser
import json

class ArithmeticExpression:
    def __init__(self, expression: str):
        self.expression = expression.strip()

    def tokenize(self):
        tokenizer = Tokenizer(self.expression)
        return tokenizer.tokenize()

    def parse(self):
        tokens = self.tokenize()
        parser = Parser(tokens)
        return parser.parse()

    def parse_as_json(self) -> str:
        try:
            tokens = self.tokenize()
            token_dicts = [
                {'type': token.type, 'value': token.value, 'position': token.position}
                for token in tokens
            ]
            return json.dumps({"tokens": token_dicts}, indent=2)
        except Exception as error:
            raise ValueError(f"Error parsing expression to JSON: {error}")