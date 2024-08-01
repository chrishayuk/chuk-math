from abc import ABC, abstractmethod
from typing import Any, Dict, List

from instructions.output_emitters.json_emitter import emit_json
from instructions.output_emitters.jsonl_emitter import emit_jsonl
from instructions.output_emitters.llama2_emitter import emit_llama2
from instructions.output_emitters.qa_emitter import emit_qa

class IInstructionEmitter(ABC):
    @abstractmethod
    def emit_instruction(self) -> Dict[str, Any]:
        pass

class InstructionEmitter(IInstructionEmitter):
    def __init__(self, ast: Dict[str, Any]):
        self.ast = ast
        self.tokens = self.ast.get('tokens', [])

    def emit_instruction(self) -> Dict[str, Any]:
        return {
            "instruction": "Base instruction",
            "ast": self.ast,
            "tokens": self.simplify_tokens(self.tokens),
            "result": {}
        }

    def simplify_tokens(self, tokens: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # Simplify tokens by removing unnecessary attributes
        return [{key: token[key] for key in token} for token in tokens]

    # Output format methods
    def emit_json(self):
        return emit_json(self.emit_instruction())

    def emit_jsonl(self):
        return emit_jsonl(self.emit_instruction())

    def emit_llama2(self):
        return emit_llama2(self.emit_instruction())

    def emit_qa(self):
        return emit_qa(self.emit_instruction())
