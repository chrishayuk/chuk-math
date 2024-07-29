# output_handlers/jsonl_handler.py
import json
from typing import Any, Dict

def output_as_jsonl(instruction: Dict[str, Any]) -> str:
    # return as jsonl
    return json.dumps(instruction) + '\n'
