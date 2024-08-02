from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Any, Dict, List
from instructions.output_emitters.json_emitter import emit_json
from instructions.output_emitters.jsonl_emitter import emit_jsonl
from instructions.output_emitters.llama2_emitter import emit_llama2
from instructions.output_emitters.qa_emitter import emit_qa

class IInstructionEmitter(ABC):
    @abstractmethod
    def emit_instruction(self, mode: str = "ast", minimal_parentheses: bool = False) -> Dict[str, Any]:
        pass

class InstructionEmitter(IInstructionEmitter):
    def __init__(self, ast: Dict[str, Any], tokens: List[Dict[str, Any]] = None):
        self.ast = ast
        self.tokens = tokens or []

    def emit_instruction(self, mode: str = "ast", minimal_parentheses: bool = False) -> Dict[str, Any]:
        if mode == "tokens":
            return self.emit_instruction_tokens()
        return self.emit_instruction_ast(minimal_parentheses)

    def emit_instruction_ast(self, minimal_parentheses: bool = False) -> Dict[str, Any]:
        explanation = self.generate_explanation()
        try:
            result = self.safe_eval(self.extract_expression_from_ast(self.ast, minimal_parentheses))
            result_str = str(result)
        except ValueError as error:
            result_str = str(error)

        return {
            "instruction": self.get_random_instruction(),
            "expression": self.extract_expression_from_ast(self.ast, minimal_parentheses),
            "tokens": self.simplify_tokens(self.tokens),
            "result": result_str,
            "explanation": explanation
        }

    def emit_instruction_tokens(self) -> Dict[str, Any]:
        return {
            "instruction": "Tokens instruction",
            "tokens": self.simplify_tokens(self.tokens),
            "result": "Tokenized form does not include evaluation"
        }

    def simplify_tokens(self, tokens: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [{key: token[key] for key in token} for token in tokens]

    def emit_json(self, mode: str = "ast", minimal_parentheses: bool = False):
        return emit_json(self.emit_instruction(mode, minimal_parentheses))

    def emit_jsonl(self, mode: str = "ast", minimal_parentheses: bool = False):
        return emit_jsonl(self.emit_instruction(mode, minimal_parentheses))

    def emit_llama2(self, mode: str = "ast", minimal_parentheses: bool = False):
        return emit_llama2(self.emit_instruction(mode, minimal_parentheses))

    def emit_qa(self, mode: str = "ast", minimal_parentheses: bool = False):
        return emit_qa(self.emit_instruction(mode, minimal_parentheses))

    def extract_expression_from_ast(self, ast, minimal_parentheses: bool = False) -> str:
        """Extracts a string representation of the expression from the AST."""
        if isinstance(ast, dict):
            if 'operator' in ast:
                left = self.extract_expression_from_ast(ast.get('left'), minimal_parentheses)
                operator = ast['operator']['value']
                right = self.extract_expression_from_ast(ast.get('right'), minimal_parentheses)
                
                if minimal_parentheses:
                    return f"{left} {operator} {right}"
                return f"({left} {operator} {right})"
            elif 'value' in ast:
                return str(ast['value'])
        return None
    
    def simplify_tokens(self, tokens: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Converts tokens into a simplified representation."""
        return [{'type': token['type'], 'value': token['value']} for token in tokens]

    def extract_expression_from_tokens(self, tokens: List[Dict[str, Any]]) -> str:
        """Extracts a string representation from tokens, preserving the original format."""
        return ' '.join(token['value'] for token in tokens)
