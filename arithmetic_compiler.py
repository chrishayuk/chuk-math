from compiler.parser.arithmetic_expression import ArithmeticExpression
from instructions.infix_expression_calculator_instruction import InfixExpressionCalculatorInstruction

class ArithmeticCompiler:
    def __init__(self, expression: str):
        # Set the expression
        self.expression = expression

        # Set up the arithmetic expression parser
        self.arithmetic_expression = ArithmeticExpression(expression)

        # Initialize
        self.ast = None
        self.json_ast = None
        self.tokens = None
        self.instruction = None

    def parse_expression(self):
        """Parse the expression into an AST and its JSON representation."""
        try:
            # Tokenize and parse the expression
            self.tokens = self.arithmetic_expression.tokenize()
            self.ast = self.arithmetic_expression.parse()
            
            # Get the AST as JSON
            self.json_ast = self.arithmetic_expression.ast_as_json()
        except Exception as e:
            print(f"Error during parsing: {e}")
            self.tokens = []
            self.ast = None
            self.json_ast = None

    def generate_instruction(self):
        """Generate instruction outputs based on the AST and tokens."""
        try:
            if self.ast and self.tokens:
                self.instruction = InfixExpressionCalculatorInstruction(self.json_ast, self.tokens)
            else:
                print("No AST or tokens available to generate instruction.")
                self.instruction = None
        except Exception as e:
            print(f"Error during instruction initialization: {e}")
            self.instruction = None

    def emit_outputs(self):
        """Emit different formats of the instruction outputs."""
        if not self.instruction:
            print("No instruction available to emit outputs.")
            return
        
        try:
            created_instruction = self.instruction.emit_instruction()
            print("\nInstruction (dictionary format):")
            print(created_instruction)

            print("\nInstruction in JSON format:")
            print(self.instruction.emit_json())

            print("\nInstruction in JSONL format:")
            print(self.instruction.emit_jsonl())

            print("\nInstruction in LLaMA2 format:")
            print(self.instruction.emit_llama2())

            print("\nInstruction in QA format:")
            print(self.instruction.emit_qa())
        except Exception as e:
            print(f"Error during instruction emission: {e}")

    def compile(self):
        """Full compilation process: parse, generate instructions, and emit outputs."""
        self.parse_expression()
        print("\nAbstract Syntax Tree (AST):")
        print(self.ast)
        print("\nAST as JSON:")
        print(self.json_ast)

        self.generate_instruction()
        self.emit_outputs()

if __name__ == "__main__":
    expression = "3 + 5 * (10 - 4)"
    compiler = ArithmeticCompiler(expression)
    compiler.compile()
