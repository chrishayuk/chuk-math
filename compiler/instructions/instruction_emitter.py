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
    def emit_instruction(self, minimal_parentheses: bool = False) -> Dict[str, Any]:
        pass

class InstructionEmitter(IInstructionEmitter):
    def __init__(self, ast: Dict[str, Any] = None, tokens: List[Any] = None, llm: str = None):
        self.ast = ast
        self.tokens = tokens or []
        
        # Set up the LLM client using LangChain
        if llm:
            self.llm = OllamaLLM(model=llm)
        else:
            self.llm = None

    def emit_instruction(self, minimal_parentheses: bool = False) -> Dict[str, Any]:
        if self.tokens:
            # extract the expression from tokens
            self.expression = self.extract_expression_from_tokens(self.tokens)
        elif self.ast:
            # extract the expression from the ast
            self.expression = self.extract_expression_from_ast(self.ast)
        else:
            self.expression = ""

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
        """Extracts a string representation of the expression from the AST."""
        if isinstance(ast, dict):
            if 'operator' in ast:
                # get the left hand of the expression
                left = self.extract_expression_from_ast(ast.get('left'))

                # get the operator
                operator = ast['operator']['value']

                # get the right hand of the expression
                right = self.extract_expression_from_ast(ast.get('right'))
                
                # return left operator right
                return f"({left} {operator} {right})"
            elif 'value' in ast:
                # return the value
                return str(ast['value'])
        return ""

    def extract_expression_from_tokens(self, tokens: list) -> str:
        """Extracts a string representation from tokens, preserving the original format."""
        expression_parts = []

        # loop the tokens
        for token in tokens:
            value = token.value
            # Remove unnecessary decimals from numbers
            if isinstance(value, float):
                value = int(value) if value.is_integer() else value
            # Add spaces around operators
            if token.type == "OPERATOR":
                expression_parts.append(f" {value} ")
            else:
                expression_parts.append(str(value))
        # Join the expression parts
        return ''.join(expression_parts).replace("( ", "(").replace(" )", ")")

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
