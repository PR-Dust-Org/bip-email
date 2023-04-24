import os

from bip import log

test_email = "philipperolet@gmail.com"


if os.path.exists("secrets"):
    secrets_table = None
else:
    import boto3
    secrets_table = (boto3.resource('dynamodb')
                     .Table(os.getenv("SECRETS_TABLE_NAME")))

# create logs directory if it doesn't exist
# if not os.path.exists("logs"):
#    os.mkdir("logs")

logger = log.create_logger("bip-email")
emails_index = "emails"
