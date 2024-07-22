import os
from dotenv import load_dotenv
from pymongo import MongoClient
import re
import nltk
nltk.download('punkt', quiet=True)
from nltk.tokenize import sent_tokenize

# Load environment variables
load_dotenv()

def remove_code_blocks(text):
    text = re.sub(r'```[\s\S]*?```', '', text)
    return text

def remove_image_links(text):
    return re.sub(r'!\[.*?\]\(.*?\)', '', text)

def remove_urls(text):
    return re.sub(r'http\S+|www.\S+', '', text)

def remove_bullet_lists(text):
    lines = text.split('\n')
    non_bullet_lines = []
    for line in lines:
        if not line.strip().startswith('-'):
            non_bullet_lines.append(line)
    return '\n'.join(non_bullet_lines)



def remove_tables(text):
    lines = text.split('\n')
    non_table_lines = []
    in_table = False
    for line in lines:
        stripped_line = line.strip()
        if stripped_line.startswith('|') and stripped_line.endswith('|'):
            in_table = True
            continue
        if in_table and set(stripped_line) <= set('- |'):
            continue
        if in_table:
            in_table = False
        non_table_lines.append(line)
    return '\n'.join(non_table_lines)


def remove_special_characters(text):
    return re.sub(r'[^a-zA-Z0-9\s.!?,]', '', text)

def remove_extra_whitespace(text):
    return re.sub(r'\s+', ' ', text).strip()

def clean_text(text):
    text = remove_code_blocks(text)
    text = remove_image_links(text)
    text = remove_urls(text)
    text = remove_tables(text)  
    text = remove_bullet_lists(text)
    text = remove_special_characters(text)
    text = remove_extra_whitespace(text)
    return text

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

def split_into_sentences(text):
    return sent_tokenize(text)

def merge_sentences(sentences, max_words=30, min_words=10):
    merged_sentences = []
    current_sentence = ""
    for sentence in sentences:
        if len(current_sentence.split()) + len(sentence.split()) <= max_words:
            if current_sentence:
                current_sentence += " "
            current_sentence += sentence
        else:
            if current_sentence:
                if len(current_sentence.split()) < min_words and merged_sentences:
                    merged_sentences[-1] += " " + current_sentence
                else:
                    merged_sentences.append(current_sentence)
            current_sentence = sentence
    
    if current_sentence:
        if len(current_sentence.split()) < min_words and merged_sentences:
            merged_sentences[-1] += " " + current_sentence
        else:
            merged_sentences.append(current_sentence)
    
    return merged_sentences

def get_sentences(text):
    clean = clean_text(text)
    sentences = split_into_sentences(clean)
    return merge_sentences(sentences)

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
body_content = remove_code_blocks(random_document.get('body', ''))
headers, body_content = extract_headers_and_content(body_content)
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