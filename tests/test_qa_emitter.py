from compiler.instructions.output_emitters.qa_emitter import emit_qa

def test_output_as_qa():
    # instruction
    instruction = {
        "instruction": "Infix expression calculation",
        "expression": '{"tokens": [1, 2, 3]}',
        "tokens": "1 + 2 * 3",
        "result": "calculated result"
    }

    # output
    expected_output = (
        "QUESTION: Infix expression calculation\n"
        "ANSWER: calculated result\n"
    )

    # compare
    assert emit_qa(instruction) == expected_output

def test_output_as_qa_with_explanation():
    # instruction with explanation
    instruction = {
        "instruction": "Infix expression calculation",
        "expression": '{"tokens": [1, 2, 3]}',
        "tokens": "1 + 2 * 3",
        "result": "calculated result",
        "explanation": "Detailed explanation here."
    }

    # output
    expected_output = (
        "QUESTION: Infix expression calculation\n"
        "ANSWER: calculated result\n"
        "EXPLANATION: Detailed explanation here.\n"
    )

    # compare
    assert emit_qa(instruction) == expected_output
