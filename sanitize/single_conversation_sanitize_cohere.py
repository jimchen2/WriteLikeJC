import json

def convert_to_cohere_format(input_file, output_file):
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        for line in infile:
            data = json.loads(line)
            
            cohere_format = {
                "messages": [
                    {
                        "role": "System",
                        "content": data["system"]
                    }
                ]
            }
            
            for message in data["messages"]:
                cohere_message = {
                    "role": "User" if message["role"] == "user" else "Chatbot",
                    "content": message["content"]
                }
                cohere_format["messages"].append(cohere_message)
            
            json.dump(cohere_format, outfile)
            outfile.write('\n')

# Usage
input_file = '../data/training_data.jsonl'  
output_file = '../data/output_cohere_single_conversation.jsonl'  

convert_to_cohere_format(input_file, output_file)
print(f"Conversion complete. Output saved to {output_file}")