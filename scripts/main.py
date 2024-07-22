import os
import json
from dotenv import load_dotenv
from pymongo import MongoClient
from clean_utils import clean_text, extract_headers_and_content, get_sentences
from question_generator import generate_question

# Load environment variables
load_dotenv()

# Use the MongoDB URI from .env
mongo_uri = os.getenv('MONGODB_URI')

# Connect to MongoDB
client = MongoClient(mongo_uri)
db = client.test

# Find a random document
random_document = list(db.documents.aggregate([{ '$sample': { 'size': 1 } }]))[0]

# Extract and clean content
doc_type = random_document.get('type', 'No type specified')
doc_title = clean_text(random_document.get('title', 'No title specified'))
headers, body_content = extract_headers_and_content(random_document.get('body', ''))
doc_body = get_sentences(body_content)

client.close()

# Prepare metadata for question generation
metadata = {
    'type': doc_type,
    'title': doc_title,
    'headers': headers
}

# Generate questions and save to file
with open('training_data.jsonl', 'w') as f:
    for sentence in doc_body:
        question = generate_question(sentence, metadata)
        json_line = {
            "system": f"Type: {doc_type}, Title: {doc_title}",
            "messages": [
                {"role": "user", "content": sentence},
                {"role": "assistant", "content": question}
            ]
        }
        f.write(json.dumps(json_line) + '\n')

print("Training data has been saved to 'training_data.jsonl'")