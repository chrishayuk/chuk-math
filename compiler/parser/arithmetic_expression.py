from compiler.lexer.tokenizer import Tokenizer, TokenizationError
from compiler.parser.parser import Parser
from decimal import Decimal
import json

from compiler.lexer.tokenizer import Tokenizer, TokenizationError
from compiler.parser.parser import Parser
from decimal import Decimal
import json

class ArithmeticExpression:
    def __init__(self, expression: str):
        # Set the expression (and strip whitespace)
        self.expression = expression.strip()
        self.tokens = []
        self.ast = None

    def tokenize(self):
        """Tokenize the expression and store the tokens."""
        try:
            # setup the tokenizer
            tokenizer = Tokenizer(self.expression)

            # tokenize
            self.tokens = tokenizer.tokenize()

            # return the tokens
            return self.tokens
        except TokenizationError as e:
            print(f"Error tokenizing expression: {e}")  # Debug statement
            raise ValueError(f"Error tokenizing expression: {e}")

    def parse(self):
        """Parse the expression into an AST and store it."""
        try:
            if not self.tokens:
                # tokenize
                self.tokenize()

            # parse
            parser = Parser(self.tokens)
            self.ast = parser.parse()

            # return the ast
            return self.ast
        except Exception as e:
            print(f"Error parsing expression: {e}")  # Debug statement
            raise ValueError(f"Error parsing expression: {e}")


    def ast_as_json(self) -> str:
        """Convert the AST into a JSON representation."""
        if not self.ast:
            self.parse()  # Ensure the AST is available
        try:
            return json.dumps(self.ast_to_dict(self.ast), indent=2)
        except Exception as e:
            raise ValueError(f"Error converting AST to JSON: {e}")

    def ast_to_dict(self, ast_node):
        """Recursively convert the AST into a dictionary."""
        if isinstance(ast_node, list):
            return [self.ast_to_dict(node) for node in ast_node]
        elif isinstance(ast_node, dict):
            return {key: self.ast_to_dict(value) for key, value in ast_node.items()}
        elif isinstance(ast_node, Decimal):
            return str(ast_node)  # Convert Decimal to string
        elif hasattr(ast_node, '__dict__'):
            return {key: self.ast_to_dict(value) for key, value in ast_node.__dict__.items()}
        else:
            return ast_node
