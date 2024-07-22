import json
import random
import os

def convert_format(input_data):
    new_format = {
        "messages": [
            {"role": "system", "content": input_data["system"]},
            *input_data["messages"]
        ]
    }
    return json.dumps(new_format)

def process_file(input_filename, train_filename, val_filename):
    with open(input_filename, 'r') as input_file:
        lines = input_file.readlines()
    
    random.shuffle(lines)
    
    total_lines = len(lines)
    train_split = int(0.9 * total_lines)
    
    train_data = lines[:train_split]
    val_data = lines[train_split:]
    
    for data, filename in [(train_data, train_filename), (val_data, val_filename)]:
        with open(filename, 'w') as output_file:
            for line in data:
                converted_data = convert_format(json.loads(line.strip()))
                output_file.write(converted_data + '\n')

data_dir = "../../data"
input_filename = os.path.join(data_dir, "training_data.jsonl")
train_filename = os.path.join(data_dir, "gpt3.5_train.jsonl")
val_filename = os.path.join(data_dir, "gpt3.5_val.jsonl")

# Ensure the data directory exists
os.makedirs(data_dir, exist_ok=True)

process_file(input_filename, train_filename, val_filename)

print(f"Conversion and splitting complete.")
print(f"Training data (90%) written to {train_filename}")
print(f"Validation data (10%) written to {val_filename}")