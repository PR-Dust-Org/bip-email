import os


test_email = "philipperolet@gmail.com"


if os.path.exists("secrets"):
    secrets_table = None
else:
    import boto3
    secrets_table = boto3.resource('dynamodb').Table(os.getenv("SECRETS_TABLE_NAME"))