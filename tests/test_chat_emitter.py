import json
from chuk_math_gym.compiler.instructions.output_emitters.chat_emitter import emit_chat


def test_emit_chat():
    """Test the chat emitter produces correct format."""
    instruction = {
        "instruction": "Calculate 2 + 3",
        "llm_step_by_step_result": "Step 1: Add 2 and 3. Result: 5",
    }

    result = emit_chat(instruction)
    parsed = json.loads(result)

    assert "messages" in parsed
    assert len(parsed["messages"]) == 2
    assert parsed["messages"][0]["role"] == "user"
    assert parsed["messages"][0]["content"] == "Calculate 2 + 3"
    assert parsed["messages"][1]["role"] == "assistant"
    assert parsed["messages"][1]["content"] == "Step 1: Add 2 and 3. Result: 5"


def test_emit_chat_with_complex_instruction():
    """Test chat emitter with more complex instruction."""
    instruction = {
        "instruction": "Solve: (3 + 5) * 2",
        "llm_step_by_step_result": "Step 1: 3 + 5 = 8\nStep 2: 8 * 2 = 16\nAnswer: 16",
    }

    result = emit_chat(instruction)
    parsed = json.loads(result)

    assert parsed["messages"][0]["content"] == "Solve: (3 + 5) * 2"
    assert "16" in parsed["messages"][1]["content"]
