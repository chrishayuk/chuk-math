import json
import sys

def convert_jsonl_to_completions(input_file, output_file):
    """
    Reads a JSONL file line by line, expecting each line to contain something like:
    {
        "messages": [
            {"role": "user", "content": "..."},
            {"role": "assistant", "content": "..."}
        ]
    }
    and outputs a JSONL file where each line has the format:
    {
        "prompt": "User content",
        "completion": "Assistant content"
    }
    """
    with open(input_file, 'r', encoding='utf-8') as fin, open(output_file, 'w', encoding='utf-8') as fout:
        for line in fin:
            line = line.strip()
            if not line:
                continue  # Skip empty lines if any

            data = json.loads(line)
            user_content = ""
            assistant_content = ""

            # Extract user and assistant messages
            for message in data.get("messages", []):
                if message.get("role") == "user":
                    user_content = message.get("content", "")
                elif message.get("role") == "assistant":
                    assistant_content = message.get("content", "")

            # Construct the new JSON record
            new_data = {
                "prompt": user_content,
                "completion": assistant_content
            }

            # Write out the new data as JSONL
            json.dump(new_data, fout, ensure_ascii=False)
            fout.write('\n')

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python convert_jsonl_to_completions.py <input_file.jsonl> <output_file.jsonl>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    convert_jsonl_to_completions(input_file, output_file)
    print(f"Conversion complete. Output written to {output_file}")
