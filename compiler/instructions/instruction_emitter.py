from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Any, Dict, List
from langchain_ollama.llms import OllamaLLM
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import PromptTemplate
from compiler.instructions.output_emitters.json_emitter import emit_json
from compiler.instructions.output_emitters.jsonl_emitter import emit_jsonl
from compiler.instructions.output_emitters.llama2_emitter import emit_llama2
from compiler.instructions.output_emitters.qa_emitter import emit_qa

class IInstructionEmitter(ABC):
    @abstractmethod
    def emit_instruction(self) -> Dict[str, Any]:
        pass

class InstructionEmitter(IInstructionEmitter):
    def __init__(self, ast: Dict[str, Any] = None, tokens: List[Any] = None, llm: str = None):
        self.ast = ast
        self.tokens = tokens or []
        self.expression = ""  # Ensure this is set

        # Set up the LLM client using LangChain
        if llm:
            self.llm = OllamaLLM(model=llm)
        else:
            self.llm = None

    def emit_instruction(self) -> Dict[str, Any]:
        # Extract the expression from the ast
        self.expression = self.extract_expression_from_ast(self.ast)

        # Simplify the tokens
        simplified_tokens = self.simplify_tokens(self.tokens)

        # Get the question
        question = self.get_random_instruction()

        # Evaluate the expression
        answer = self.evaluate_expression()

        # Generate the explanation
        explanation = self.generate_explanation()

        # Generate LLM responses only if an LLM is provided
        if self.llm:
            pretty_result = self.get_pretty_result(question, answer)
            step_by_step_result = self.get_step_by_step_explanation(question, answer, explanation)
        else:
            pretty_result = step_by_step_result = None

        # Initialize the instruction dictionary
        instruction = {
            "instruction": question,
            "expression": self.expression,
            "tokens": simplified_tokens,
            "ast": self.ast,
            "result": answer,
            "explanation": explanation,
            "llm_pretty_result": pretty_result,
            "llm_step_by_step_result": step_by_step_result
        }

        return instruction

    

    def simplify_tokens(self, tokens: List[Any]) -> List[Dict[str, Any]]:
        """Converts tokens into a simplified representation."""
        return [{'type': token.type, 'value': token.value} for token in tokens]

    def emit_json(self):
        # emity json
        return emit_json(self.emit_instruction())

    def emit_jsonl(self):
        # emit jsonl
        return emit_jsonl(self.emit_instruction())

    def emit_llama2(self):
        # emit llama2
        return emit_llama2(self.emit_instruction())

    def emit_qa(self):
        # emit qs
        return emit_qa(self.emit_instruction())

    def extract_expression_from_ast(self, ast) -> str:
        """Extracts a string representation of the expression from the AST with minimal parentheses."""
        if isinstance(ast, dict):
            if 'operator' in ast:
                # Recursively get the left and right parts of the expression
                left = self.extract_expression_from_ast(ast.get('left'))
                operator = ast['operator']['value']
                right = self.extract_expression_from_ast(ast.get('right'))
                
                # Determine if parentheses are needed
                left_needs_paren = self._needs_parentheses(ast.get('left'), ast['operator']['value'])
                right_needs_paren = self._needs_parentheses(ast.get('right'), ast['operator']['value'])

                # Return the expression with necessary parentheses
                return f"{'(' if left_needs_paren else ''}{left}{')' if left_needs_paren else ''} {operator} {'(' if right_needs_paren else ''}{right}{')' if right_needs_paren else ''}"
            elif 'value' in ast:
                value = ast['value']
                # Convert the value to a string without unnecessary decimal places
                if isinstance(value, float) and value.is_integer():
                    value = int(value)
                return str(value)
        return ""


    def _needs_parentheses(self, sub_ast, parent_op) -> bool:
        """Determines if the sub-expression needs parentheses based on the parent operator."""
        if not sub_ast or not isinstance(sub_ast, dict):
            return False
        if 'operator' not in sub_ast:
            return False

        child_op = sub_ast['operator']['value']

        # Define precedence rules
        precedence = {
            '+': 1, '-': 1,
            '*': 2, '/': 2,
            '^': 3
        }
        
        # Check if child operator has lower precedence than parent operator
        return precedence.get(child_op, 0) < precedence.get(parent_op, 0)

    def evaluate_expression(self) -> str:
        """Evaluates the expression and returns the result as a string."""
        try:
            # evaluate the expression
            result = self.safe_eval(self.expression)

            # return the result
            return str(result)
        except ValueError as error:
            # return the result
            return str(error)
        
    def get_pretty_result(self, question, answer):
        """Generate a natural language response using the question and answer."""
        response_template = """For the question "{question}" and it's associated expression "{expression}", the result is "{answer}".  Now create a highly readable version of the answer, keep it simple, not LATEX.  Just provide the answer response, no premable, do not change the values for the question or expression."""
        
        # call the llm
        return self.get_llm_response(response_template.format(expression=self.expression, answer=answer, question=question))

    def get_step_by_step_explanation(self, question, answer, explanation) -> str:
        """Generate a step-by-step explanation using the explanation."""
        response_template = """or the question "{question}" and it's associated expression "{expression}", the result is "{answer}.  The following is the step by step explanation: {explanation}.  Now create a highly readable version of the answer, with a highly readable step by step explanation, using the provided explanation, keep it simple, not LATEX.  Just provide the answer response, no premable.  Provide the step by step analysis before providing the answer"""

        # call the llm
        return self.get_llm_response(response_template.format(expression=self.expression, answer=answer, question=question, explanation=explanation))
    
    def get_llm_response(self, input_text: str) -> str:
        """Get a response from the LLM."""
        if self.llm:
            try:
                # Setup the prompt and chain
                prompt = PromptTemplate(input_variables=["input_text"], template="{input_text}")
                chain = prompt | self.llm | StrOutputParser()

                # Execute the chain
                response = chain.invoke({"input_text": input_text})
                return response
            except Exception as e:
                return f"Error generating response from LLM: {e}"
        else:
            return input_text  # Fallback to input if LLM is not available
