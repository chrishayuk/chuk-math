from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Any, Dict, List
from langchain_ollama.llms import OllamaLLM
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
        # extract the expression from the ast
        self.expression = self.extract_expression_from_ast(self.ast)

        # simplify the tokens
        simplified_tokens = self.simplify_tokens(self.tokens)

        # generate the explanation
        explanation = self.generate_explanation()

        # evaluate the expression
        result_str = self.evaluate_expression()

        # return the instruction
        return {
            "instruction": self.get_random_instruction(True),
            "expression": self.expression,
            "tokens": simplified_tokens,
            "result": result_str,
            "explanation": explanation
        }

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
