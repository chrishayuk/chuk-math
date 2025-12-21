import sys
import json
import random

def merge_and_randomize_jsonl_files(output_file="output/merged.jsonl"):
    # Grab filenames from command-line args (excluding the script name)
    filenames = sys.argv[1:]
    
    all_records = []

    # Read each file and extend the all_records list
    for filename in filenames:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:  # Only process non-empty lines
                    all_records.append(json.loads(line))

    # Randomize the combined data
    random.shuffle(all_records)

    # Write out to the merged JSONL file
    with open(output_file, 'w', encoding='utf-8') as out_f:
        for record in all_records:
            out_f.write(json.dumps(record, ensure_ascii=False) + '\n')

if __name__ == "__main__":
    merge_and_randomize_jsonl_files()
