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

def process_document(args):
    sentences, metadata, doc_type, doc_title = args
    interactions = []
    for sentence in sentences:
        question = generate_question(sentence, metadata)
        interactions.append({"role": "user", "content": question})
        interactions.append({"role": "assistant", "content": sentence})
    
    json_line = {
        "system": f"You are talking to Jim Chen about {doc_type}, titled '{doc_title}'.",
        "messages": interactions
    }
    print(f"Generated {len(interactions)//2} interactions for '{doc_title}'")
    print("---")
    return json.dumps(json_line)

# Query for documents with access field equal to 1
documents = list(db.documents.find({'access': 1}))

# Prepare training data for each document
with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
    future_to_doc = {}
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

        # Prepare arguments for processing
        args = (doc_body, metadata, doc_type, doc_title)
        
        # Submit the document for processing
        future = executor.submit(process_document, args)
        future_to_doc[future] = doc_title

    # Write results to file as they complete
    with open('../../data/full_conversation_training_data.jsonl', 'a') as f:
        for future in concurrent.futures.as_completed(future_to_doc):
            doc_title = future_to_doc[future]
            try:
                result = future.result()
                f.write(result + '\n')
                print(f"Completed processing for '{doc_title}'")
            except Exception as exc:
                print(f'{doc_title} generated an exception: {exc}')

client.close()
print("Training data generation complete. Data saved to 'training_data.jsonl'.")