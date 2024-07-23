import json
import random
import os

def convert_to_gpt_format(input_file, train_file, valid_file):
    train_data = []
    valid_data = []

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
            
            # Randomly assign to validation (10%) or training (90%) set
            if random.random() < 0.1:
                valid_data.append(gpt_format)
            else:
                train_data.append(gpt_format)

    # Ensure output directory exists
    output_dir = os.path.dirname(os.path.abspath(train_file))
    os.makedirs(output_dir, exist_ok=True)

    # Write training data
    with open(train_file, 'w') as outfile:
        for item in train_data:
            json.dump(item, outfile)
            outfile.write('\n')

    # Write validation data
    with open(valid_file, 'w') as outfile:
        for item in valid_data:
            json.dump(item, outfile)
            outfile.write('\n')

# Usage
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))

input_file = os.path.join(project_root, "data", "training_data.jsonl")
train_file = os.path.join(project_root, "data", "single_conversation_gpt3.5train.jsonl")
valid_file = os.path.join(project_root, "data", "single_conversation_gpt3.5var.jsonl")

convert_to_gpt_format(input_file, train_file, valid_file)
print(f"Conversion complete.")
print(f"Training data written to {train_file}")
print(f"Validation data written to {valid_file}")