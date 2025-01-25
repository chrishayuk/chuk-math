import json
import random
from decimal import Decimal, InvalidOperation, getcontext
from langchain_ollama import OllamaLLM
from sympy import sympify, SympifyError
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import PromptTemplate
from compiler.instructions.instruction_emitter import InstructionEmitter
from explanations.expression_explanation_generator import ExpressionExplanationGenerator
from explanations.expression_node import ExpressionNode
from explanations.expression_tree import ExpressionTree

class InfixExpressionCalculatorInstruction(InstructionEmitter):
    def __init__(self, ast: dict, tokens: list = None, llm: str = None):
        # Check if we're parsing an ast or tokens
        if isinstance(ast, str):
            ast = json.loads(ast)

        # Call the parent constructor
        super().__init__(ast, tokens or [], llm)

        # Set the tokens
        self.tokens = tokens or []

    def get_random_instruction(self, use_llm=False) -> str:
        # Get the instruction templates
        templates = [
            lambda: f"Calculate the result of the expression: {self.expression}.",
            lambda: f"Solve the following expression: {self.expression}.",
            lambda: f"Evaluate the expression: {self.expression}.",
            lambda: f"Find the result of {self.expression}.",
            lambda: f"What is the value of {self.expression}?",
            lambda: f"{self.expression}",
            lambda: f"Solve the expression: {self.expression}",
            lambda: f"{self.expression}: what's the answer?",
            lambda: f"Calculate {self.expression}.",
            lambda: f"What's {self.expression}?",
            lambda: f"Figure out the answer to {self.expression}",
            lambda: f"What is {self.expression} equal to?",
            lambda: f"Work out what {self.expression} is?",
            lambda: f"Work out {self.expression} and display the answer",
            lambda: f"Solve {self.expression}.",
            lambda: f"Tell me what {self.expression} is",
            lambda: f"Resolve {self.expression} and note the result.",
            lambda: f"Evaluate: {self.expression}.",
            lambda: f"Solve the arithmetic expression {self.expression}.",
            lambda: f"Calculate {self.expression} and show the result",
            lambda: f"What does the expression {self.expression} equal?",
            lambda: f"Find the value of this arithmetic challenge: {self.expression}.",
            lambda: f"Determine the outcome of the expression {self.expression}",
            lambda: f"For the arithmetic problem {self.expression}, what's the answer?",
            lambda: f"Work out the expression {self.expression}.",
            lambda: f"What result does {self.expression} yield?",
            lambda: f"Evaluate this: {self.expression} and return the result",
        ]

        # Shuffle templates to increase randomness
        random.shuffle(templates)   

        # get a random template
        template = random.choice(templates)()

        # If use_llm is True and llm is set up, fetch instruction from LLM
        if use_llm and self.llm:
            # get instruction from llm
            template = self.get_instruction_from_llm(template)

        # return the template
        return template

    def get_instruction_from_llm(self, question: str) -> str:
        # prompt template
        prompt_template = """Generate a question for the following mathematical expression: {expression}.  
            Ensure it's accurate, do not miss any values.  Do NOT change parenthesis in the expression.  Ensure random
            Example: {question}
            Question: """

        try:
            # Use the expression in the context
            prompt = PromptTemplate(input_variables=["expression", "question"], template=prompt_template)

            # setup the chain
            chain = prompt | self.llm | StrOutputParser()

            # execute
            response = chain.invoke({"expression":self.expression, "question":question})

            # return the response
            return response
        except Exception as e:
            return f"Error generating instruction from LLM: {e}"
        

    def safe_eval(self, expression: str) -> Decimal:
        try:
            # Evaluate expression
            sympy_expr = sympify(expression)

            # Check for an error
            if sympy_expr is None:
                raise ValueError("Invalid expression resulting in None")

            # Get the result
            result = sympy_expr.evalf()

            # Return the value
            getcontext().prec = 64
            decimal_result = Decimal(str(result))
            return decimal_result.quantize(Decimal('1.0000')).normalize()
        except (SympifyError, InvalidOperation, ValueError) as error:
            raise ValueError(f"Invalid expression or calculation error: {error}")

    def generate_explanation(self):
        """Generate an explanation for the evaluated expression."""
        # Convert AST to ExpressionTree
        tree = self.ast_to_expression_tree(self.ast)

        # Generate explanation
        explanation_generator = ExpressionExplanationGenerator(tree.root)
        explanation_text, result = explanation_generator.generate_explanation(0)

        return explanation_text

    def ast_to_expression_tree(self, ast_node) -> ExpressionTree:
        """Converts an AST to an ExpressionTree."""
        if not ast_node:
            return None

        def build_expression_node(node):
            # Handle binary expressions
            if node.get("type") == "BinaryExpression":
                return ExpressionNode(
                    value=node["operator"]["value"],  # e.g. '+', '-', '*', '/'
                    left=build_expression_node(node["left"]),
                    right=build_expression_node(node["right"])
                )

            # Handle unary expressions (e.g. -5) if your parser produces them
            elif node.get("type") == "UnaryExpression":
                # Typically, you’ll have node["operator"] and node["argument"]
                return ExpressionNode(
                    value=node["operator"]["value"],  # e.g. '-'
                    left=build_expression_node(node["operand"]),
                    right=None
                )

            # Handle simple literals
            elif node.get("type") == "Literal":
                return ExpressionNode(value=node["value"])

            # Fallback: If the parser doesn’t always set "type", or uses a different structure
            # but sets "operator" or "value" directly, you can check for them here:
            elif "operator" in node and "left" in node and "right" in node:
                # If your parser only sets "operator" for a proper binary expression
                return ExpressionNode(
                    value=node["operator"]["value"],
                    left=build_expression_node(node["left"]),
                    right=build_expression_node(node["right"])
                )
            elif "value" in node:
                # Then it’s presumably a literal
                return ExpressionNode(value=node["value"])

            return None

        expression_tree = ExpressionTree()
        expression_tree.root = build_expression_node(ast_node)
        return expression_tree

