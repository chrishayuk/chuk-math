import json

from output_handlers.json_handler import output_as_json

def test_output_as_json():
    # set the instruction
    instruction = {
        "instruction": "Infix expression calculation",
        "expression": '{"tokens": [1, 2, 3]}',
        "tokens": "1 + 2 * 3",
        "result": "calculated result"
    }

    # generate the output
    expected_output = json.dumps(instruction, indent=2)

    # return as json
    assert output_as_json(instruction) == expected_output
