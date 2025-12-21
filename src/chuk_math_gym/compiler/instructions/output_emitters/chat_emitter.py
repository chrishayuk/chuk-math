# output_handlers/chat_emitter.py
import json
from typing import Any, Dict

def emit_chat(instruction: Dict[str, Any]) -> str:
    chat_output = {
        "messages": [
            {
                "role": "user",
                "content": instruction["instruction"]
            },
            {
                "role": "assistant",
                "content": instruction["llm_step_by_step_result"]
            }
        ]
    }
    return json.dumps(chat_output)
