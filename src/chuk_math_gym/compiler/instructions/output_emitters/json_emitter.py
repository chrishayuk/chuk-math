# output_handlers/json_handler.py
import json
from typing import Any, Dict

def emit_json(instruction: Dict[str, Any]) -> str:
    # return as json
    return json.dumps(instruction, indent=2)
