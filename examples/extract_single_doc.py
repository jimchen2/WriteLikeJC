from pymongo import MongoClient
import getpass

# Prompt for the MongoDB URI and mask the input
mongo_uri = getpass.getpass("Please enter your MongoDB URI: ")

# Connect to MongoDB
client = MongoClient(mongo_uri)

# Select the database
db = client.test

# Fetch one document from the 'documents' collection
document = db.documents.find_one()

# Extract type, title, and body
doc_type = document.get('type', 'No type specified')
doc_title = document.get('title', 'No title specified')
doc_body = document.get('body', 'No body content')

# Close the connection
client.close()

# Print the extracted information
print(f"Type: {doc_type}\n")
print(f"Title: {doc_title}\n")
print("Body:")
print(doc_body)