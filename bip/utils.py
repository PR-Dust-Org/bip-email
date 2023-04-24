import os.path
import openai
import tiktoken

from bip.config import secrets_table, logger

secrets_dir = 'secrets'


def get_secret(key_name):
    """Get a secret value from the DynamoDB secrets database or from a file in
    the secrets directory if the secrets table is not defined

    :param key_name: The name of the secret to get.
    """
    if not secrets_table:
        with open(os.path.join(secrets_dir, f"{key_name}.txt")) as f:
            return f.read().strip()
    else:
        return secrets_table.get_item(
            Key={'key': key_name}
        )['Item']['value']


def set_secret(key_name, value):
    """Set a secret value in the dynamodb secrets database or in a file in the
    secrets directory if the secrets table is not defined

    :param key_name: The name of the secret to set.
    :param value: The value of the secret to set.
    """
    if not secrets_table:
        with open(os.path.join(secrets_dir, f"{key_name}.txt"), 'w') as f:
            f.write(value)
    else:
        secrets_table.put_item(
            Item={
                'key': key_name,
                'value': value
            }
        )


def embed(texts):
    """Embed a text using OpenAI's API"""
    logger.info(
        f"Embedding {len(texts) if isinstance(texts, list) else 1} text(s)")
    response = openai.Embedding.create(
        input=texts,
        model="text-embedding-ada-002")
    return [x['embedding'] for x in response['data']]


def count_tokens(text, model="text-davinci-003"):
    return len(tiktoken.encoding_for_model(model).encode(text))


def tokenize(text, model="text-davinci-003"):
    return tiktoken.encoding_for_model(model).encode(text)


def detokenize(tokens, model="text-davinci-003"):
    return tiktoken.encoding_for_model(model).decode(tokens)
