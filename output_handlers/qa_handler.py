# output_handlers/qa_handler.py
from typing import Any, Dict

def output_as_qa(instruction: Dict[str, Any]) -> str:
    # set in qa format
    qa = f"QUESTION: {instruction['instruction']}\nANSWER: {instruction['result']}\n"

    # check if we have an explanation
    if 'explanation' in instruction:
        # add the explanation
        qa += f"EXPLANATION: {instruction['explanation']}\n"

    # return in QA format
    return qa
