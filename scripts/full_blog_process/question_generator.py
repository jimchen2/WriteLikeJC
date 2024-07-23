import os
import json
import boto3
from dotenv import load_dotenv
from botocore.exceptions import ClientError

# Load environment variables
load_dotenv()

# Set up Amazon Bedrock client
bedrock = boto3.client(
    service_name='bedrock-runtime',
    region_name=os.getenv('AWS_REGION', 'us-east-1'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)

def generate_question(sentence, metadata):
    prompt = f"""Generate a specific question for which the given sentence is the appropriate answer. Use the metadata for context.

Answer: "{sentence}"

Metadata:
Type: {metadata['type']}
Title: {metadata['title']}

Guidelines:
1. Question should be specific to the answer.
2. Use key information from the answer.
3. Avoid yes/no questions.
4. Ensure relevance to metadata context.
5. Avoid using words from the answer.

Return only the question, make the question concise without any additional text
"""
    # Format the request payload using the model's native structure
    native_request = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 512,
        "temperature": float(os.getenv('TEMPERATURE', 0.7)),
        "messages": [
            {
                "role": "user",
                "content": [{"type": "text", "text": prompt}],
            }
        ],
    }

    request = json.dumps(native_request)

    response = bedrock.invoke_model(
        modelId=os.getenv('BEDROCK_MODEL_ID'),
        body=request
    )

    model_response = json.loads(response["body"].read())

    return model_response["content"][0]["text"].strip()


def generate_questions_for_sentences(sentences, metadata):
    questions = []
    for sentence in sentences:
        question = generate_question(sentence, metadata)
        if question:
            questions.append(question)
    return questions
