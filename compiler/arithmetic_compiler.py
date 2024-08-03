from compiler.instructions.math_problem_instruction import MATHProblemInstruction
from compiler.parser.arithmetic_expression import ArithmeticExpression
from compiler.instructions.infix_expression_calculator_instruction import InfixExpressionCalculatorInstruction

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

    def generate_instruction(self, llm: str):
        """Generate instruction outputs based on the AST and tokens."""
        try:
            # ensure we have an ast or tokens
            if self.ast and self.tokens:
                # set the instruction
                self.instruction = InfixExpressionCalculatorInstruction(self.json_ast, self.tokens, llm=llm)
                #self.instruction = MATHProblemInstruction(self.json_ast, self.tokens, llm=llm)
            else:
                print("No AST or tokens available to generate instruction.")
                self.instruction = None
        except Exception as e:
            print(f"Error during instruction initialization: {e}")
            self.instruction = None


    def compile(self):
        """Full compilation process: parse, generate instructions, and emit outputs."""
        # Parse the expression
        self.parse_expression()

        # Generate the instruction
        self.generate_instruction(None)  # Assuming no specific LLM provided

        # Generate instruction using the instruction object
        if self.instruction:
            instruction_output = self.instruction.emit_instruction()
        else:
            instruction_output = {}

        print("Instruction:")
        print(instruction_output)
