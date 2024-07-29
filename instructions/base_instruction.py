# base_instruction.py
import json
from abc import ABC, abstractmethod
from typing import Any, Dict, List

from output_handlers.json_handler import output_as_json
from output_handlers.jsonl_handler import output_as_jsonl
from output_handlers.llama2_handler import output_as_llama2
from output_handlers.qa_handler import output_as_qa

class IInstruction(ABC):
    @abstractmethod
    def create_instruction(self) -> Dict[str, Any]:
        pass

class BaseInstruction(IInstruction):
    def __init__(self, expression: str, original_expression: str):
        self.expression = expression
        self.original_expression = original_expression
        parsed = json.loads(expression)
        self.tokens = parsed['tokens']

    def create_instruction(self) -> Dict[str, Any]:
        return {
            "instruction": "Base instruction",
            "expression": self.expression,
            "tokens": self.original_expression,
            "result": {}
        }
    
    def simplify_tokens(self, tokens: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # simplified tokens
        simplified_tokens = []
        
        # loop through the tokens
        for token in tokens:
            # remove tokens that are formatting
            simplified_token = {key: token[key] for key in token if key not in ['offset', 'lineBreaks', 'line', 'col']}

            # add the simplified tokens only
            simplified_tokens.append(simplified_token)

        # return the simplfiied token list
        return simplified_tokens
    
    # Example usage of output handlers
    def to_json(self):
        # return the output as json
        return output_as_json(self.create_instruction())

    def to_jsonl(self):
        # return the output as jsonl
        return output_as_jsonl(self.create_instruction())

    def to_llama2(self):
        # return the output as llama2
        return output_as_llama2(self.create_instruction())

    def to_qa(self):
        # return the output as qa format
        return output_as_qa(self.create_instruction())
