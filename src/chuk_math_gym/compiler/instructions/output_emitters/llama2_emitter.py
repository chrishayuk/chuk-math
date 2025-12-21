# output_handlers/llama2_handler.py
from typing import Any, Dict

def emit_llama2(instruction: Dict[str, Any]) -> str:
    # return in llama2 instruction format
    return f"<s>[INST]{instruction['instruction']}[/INST] {instruction['result']}</s>\n"
