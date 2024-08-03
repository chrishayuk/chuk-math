import json
import random
from decimal import Decimal, InvalidOperation, getcontext
from sympy import sympify, SympifyError
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import PromptTemplate
from compiler.instructions.instruction_emitter import InstructionEmitter

class MATHProblemInstruction(InstructionEmitter):
    def __init__(self, ast: dict, tokens: list = None, llm: str = None):
        # Check if we're parsing an ast or tokens
        if isinstance(ast, str):
            ast = json.loads(ast)

        # Call the parent constructor
        super().__init__(ast, tokens or [], llm)

        # Set the tokens
        self.tokens = tokens or []

    def get_random_instruction(self, use_llm=False) -> dict:
        # get the template
        template = {
            "instruction": f"Solve for the value of the expression: {self.expression}.",
            "expression": self.expression
        }

        if use_llm and self.llm:
            refined_problem = self.get_instruction_from_llm(template["instruction"])
            if not refined_problem.startswith("Error"):
                template["instruction"] = refined_problem

        return template

    def get_instruction_from_llm(self, question: str) -> str:
        prompt_template = """Based on the following mathematical expression, generate a problem similar to those found in the MATH dataset. The problem should include a real-world scenario and a narrative.
        
        Examples of MATH problems:
        1. "A rectangle has a length that is three times its width. If the width is 4 meters, what is the area of the rectangle?"
        2. "John has three times as many apples as Jane. If Jane has x apples, how many apples do they have in total if John gives 2 apples to Jane?"
        3. "The sum of the squares of two consecutive odd numbers is 290. What are the numbers?"

        Ensure it is accurate, do not miss any values.  Ensure random
        The generated problem must be an accurate representation of the expression.
        DO NOT ATTEMPT TO SOLVE THE PROBLEM.
        You can can use a scratchpad to think this through, double check and revise
        <ScratchPad></ScratchPad>
        Check the output and revise, put the final answer in these tags
        <FinalAnswer></FinalAnswer>

        Given Expression: {expression}
        Problem: """

        try:
            prompt = PromptTemplate(input_variables=["expression", "question"], template=prompt_template)
            
            # Assuming that the llm provided is a valid object handled outside of this code snippet
            chain = prompt | self.llm | StrOutputParser()

            response = chain.invoke({"expression": self.expression, "question": question})

            return response
        except Exception as e:
            return f"Error generating instruction from LLM: {e}"

    def safe_eval(self, expression: str) -> Decimal:
        try:
            sympy_expr = sympify(expression)
            if sympy_expr is None:
                raise ValueError("Invalid expression resulting in None")
            result = sympy_expr.evalf()
            getcontext().prec = 64
            decimal_result = Decimal(str(result))
            return decimal_result.quantize(Decimal('1.0000')).normalize()
        except (SympifyError, InvalidOperation, ValueError) as error:
            raise ValueError(f"Invalid expression or calculation error: {error}")

    def generate_explanation(self):
        return "This explanation details the steps taken to evaluate the expression."

