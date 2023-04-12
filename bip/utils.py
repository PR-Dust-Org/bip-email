import os.path
import openai


def get_secret_key(key_name, key_dir='secrets'):
    """Get API key from secrets/{key_name}-key.txt"""
    with open(os.path.join(key_dir,f"{key_name}-key.txt")) as f:
        return f.read().strip()


def embed(text):
    """Embed a text using OpenAI's API"""
    response = openai.Embedding.create(
        input=text,
        model="text-embedding-ada-002")
    return response['data'][0]['embedding']