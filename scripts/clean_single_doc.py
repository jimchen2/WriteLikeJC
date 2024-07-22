import os
from dotenv import load_dotenv
from pymongo import MongoClient
import re
import nltk
nltk.download('punkt', quiet=True)
from nltk.tokenize import sent_tokenize

# Load environment variables
load_dotenv()

def clean_text(text):
    # Remove image links and bullet points
    text = re.sub(r'!\[.*?\]\(.*?\)|\n\s*-\s*', '', text)
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove URLs
    text = re.sub(r'http\S+|www.\S+', '', text)
    # Remove special characters except period, question mark, and exclamation mark
    text = re.sub(r'[^a-zA-Z0-9\s.!?#]', '', text)
    return text.strip()

def extract_headers_and_content(text):
    lines = text.split('\n')
    headers = []
    content = []
    for line in lines:
        if line.strip().startswith('#'):
            headers.append(clean_text(line))
        else:
            content.append(line)
    return headers, '\n'.join(content)

def get_sentences(text):
    clean = clean_text(text)
    sentences = sent_tokenize(clean)
    return [s.strip() for s in sentences if s.strip()]

# Use the MongoDB URI from .env
mongo_uri = os.getenv('MONGODB_URI')

# Connect to MongoDB
client = MongoClient(mongo_uri)
db = client.test
document = db.documents.find_one()

# Extract and clean content
doc_type = document.get('type', 'No type specified')
doc_title = clean_text(document.get('title', 'No title specified'))
headers, body_content = extract_headers_and_content(document.get('body', ''))
doc_body = get_sentences(body_content)

client.close()

# Print the cleaned up information
print("Metadata:")
print(f"Type: {doc_type}")
print(f"Title: {doc_title}")
print("Headers:")
for header in headers:
    print(f"- {header}")

print("\nDocument sentences:")
for i, sentence in enumerate(doc_body, 1):
    print(f"{i}. {sentence}")