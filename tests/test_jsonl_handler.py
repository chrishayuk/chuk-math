import json
from output_handlers.jsonl_handler import output_as_jsonl

def test_output_as_jsonl():
    # set the instruction
    instruction = {
        "instruction": "Infix expression calculation",
        "expression": '{"tokens": [1, 2, 3]}',
        "tokens": "1 + 2 * 3",
        "result": "calculated result"
    }

    # set the expected output
    expected_output = json.dumps(instruction) + '\n'

    # compare
    assert output_as_jsonl(instruction) == expected_output
