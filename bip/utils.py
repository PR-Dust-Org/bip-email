import os.path
import openai

secrets_dir = 'secrets'

def get_secret(key_name):
    with open(os.path.join(secrets_dir,f"{key_name}.txt")) as f:
        return f.read().strip()


def set_secret(key_name, value):
    with open(os.path.join(secrets_dir,f"{key_name}.txt"), 'w') as f:
        f.write(value)


def embed(text):
    """Embed a text using OpenAI's API"""
    response = openai.Embedding.create(
        input=text,
        model="text-embedding-ada-002")
    return response['data'][0]['embedding']