from output_handlers.llama2_handler import output_as_llama2

def test_output_as_llama2():
    # set the instruction
    instruction = {
        "instruction": "Infix expression calculation",
        "expression": '{"tokens": [1, 2, 3]}',
        "tokens": "1 + 2 * 3",
        "result": "calculated result"
    }

    # set the expected output
    expected_output = "<s>[INST]Infix expression calculation[/INST] calculated result</s>\n"

    # compare
    assert output_as_llama2(instruction) == expected_output
