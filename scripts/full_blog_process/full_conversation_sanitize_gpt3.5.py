import json
import os

def convert_to_gpt_format(input_file, output_file):
    output_data = []

    with open(input_file, 'r') as infile:
        for line in infile:
            data = json.loads(line)
            
            system_message = data.get("system", "")
            messages = data.get("messages", [])
            
            gpt_format = {
                "messages": [
                    {"role": "system", "content": system_message}
                ]
            }
            
            for msg in messages:
                gpt_format["messages"].append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            output_data.append(gpt_format)

    # Ensure output directory exists
    output_dir = os.path.dirname(os.path.abspath(output_file))
    os.makedirs(output_dir, exist_ok=True)

    # Write output data
    with open(output_file, 'w') as outfile:
        for item in output_data:
            json.dump(item, outfile)
            outfile.write('\n')

# Usage
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..', '..'))

input_file = os.path.join(project_root, "data", "full_conversation_training_data.jsonl")
output_file = os.path.join(project_root, "data", "full_conversation_gpt3.5.jsonl")

convert_to_gpt_format(input_file, output_file)
print(f"Conversion complete.")
print(f"Output data written to {output_file}")