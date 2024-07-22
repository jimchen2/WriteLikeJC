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
    prompt = f"""You are an AI assistant tasked with generating a specific and accurate question 
    based on a given answer. The provided sentence is the answer, and your task is to create a question
    that would naturally lead to this answer. Use the provided metadata for context.

Given answer: "{sentence}"

Metadata (for context):
Type: {metadata['type']}
Title: {metadata['title']}
Headers: {', '.join(metadata['headers'])}

Guidelines:
1. The question should be specific enough that the given sentence is the most appropriate answer.
2. Use key information from the answer to formulate the question.
3. Ensure the question cannot be answered by a simple yes or no.
4. The question should be relevant to the context provided in the metadata.
5. Avoid using the exact wording from the answer in the question.

Generate a single, specific question for which the given sentence is the most appropriate answer. 
Return only the question itself, without any additional text or explanation.
Return only the question itself, without any introductory phrases or additional text.
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
