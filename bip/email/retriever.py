# This module keeps an up-to-date vector database of email content usable by
# the email chatbot
from datetime import datetime

from bip.email import gmail
from bip.email.store import store_in_chroma_db

def _get_last_update_date():
    """Return last time DB was updated
    :return datetime.datetime"""
    # TODO
    return datetime.datetime(2023, 3, 28, 0, 0, 0)


def update_email_database(gmail_client, database):
    last_update_date = _get_last_update_date()
    new_messages = gmail.get_last_emails(gmail_client, last_update_date)
    for message in new_messages:
        database.store(message)