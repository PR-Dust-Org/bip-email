import os.path
import openai

from bip.config import secrets_table

secrets_dir = 'secrets'

def get_secret(key_name):
    """Get a secret value from the DynamoDB secrets database or from a file in the 
    secrets directory if the secrets table is not defined
    
    :param key_name: The name of the secret to get.
    """
    if not secrets_table:
        with open(os.path.join(secrets_dir,f"{key_name}.txt")) as f:
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
        with open(os.path.join(secrets_dir,f"{key_name}.txt"), 'w') as f:
            f.write(value)
    else:
        secrets_table.put_item(
            Item={
                'key': key_name,
                'value': value
            }
        )


def embed(text):
    """Embed a text using OpenAI's API"""
    response = openai.Embedding.create(
        input=text,
        model="text-embedding-ada-002")
    return response['data'][0]['embedding']