import json

from instructions.output_emitters.json_emitter import emit_json

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
    assert emit_json(instruction) == expected_output
