import os
import json
from dotenv import load_dotenv
from pymongo import MongoClient
from clean_utils import clean_text, extract_headers_and_content, get_sentences
from question_generator import generate_question
import concurrent.futures

# Load environment variables
load_dotenv()

# Use the MongoDB URI from .env
mongo_uri = os.getenv('MONGODB_URI')

# Connect to MongoDB
client = MongoClient(mongo_uri)
db = client.test

def process_sentence(args):
    sentence, metadata, doc_type, doc_title = args
    question = generate_question(sentence, metadata)
    json_line = {
        "system": f"You are talking to Jim Chen about {doc_type}, titled '{doc_title}'.",
        "messages": [
            {"role": "assistant", "content": question},
            {"role": "user", "content": sentence}
        ]
    }
    print(f"Q: {question}")
    print(f"A: {sentence}")
    print("---")
    return json.dumps(json_line)

# Query for documents with access field equal to 1
documents = list(db.documents.find({'access': 1}))

# Prepare training data for each document
for document in documents:
    # Extract and clean content
    doc_type = document.get('type', 'No type specified')
    doc_title = clean_text(document.get('title', 'No title specified'))
    headers, body_content = extract_headers_and_content(document.get('body', ''))
    doc_body = get_sentences(body_content)

    # Prepare metadata for question generation
    metadata = {
        'type': doc_type,
        'title': doc_title,
        'headers': headers
    }
    print(json.dumps(metadata, indent=2))

    print(f"Generating training data for document: {doc_title}")

    # Prepare arguments for parallel processing
    args_list = [(sentence, metadata, doc_type, doc_title) for sentence in doc_body]

    # Process sentences in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        results = list(executor.map(process_sentence, args_list))

    # Write results to file
    with open('training_data.jsonl', 'a') as f:
        for result in results:
            f.write(result + '\n')

client.close()
print("Training data generation complete. Data saved to 'training_data.jsonl'.")