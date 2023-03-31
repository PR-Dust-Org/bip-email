# This module retrieves emails from a gmail account and stores them in a
# vector store
import pinecone
from langchain.embeddings import OpenAIEmbeddings

from bip.email import gmail


def get_pinecone_key():
    """Get Pinecone API key from secrets/pinecone-key.txt"""
    with open('../secrets/pinecone-key.txt') as f:
        return f.read().strip()


class Retriever():
    BATCH_SIZE = 100

    def __init__(self):
        self._gmail_client = gmail.gmail_api_client()
        pinecone.init(api_key=get_pinecone_key(), environment="eu-west1-gcp")
        self._index = pinecone.Index("bip-email")
        self._embeddings = OpenAIEmbeddings()

    def _already_fully_stored(self, email_batch):
        """Check if the email batch is already fully stored in the index.

        Since we store the emails in batches,  and assume they are sorted by
        descending date, we can check if the first and last emails of the batch
        are already stored.
        Since the index stores message chunks, not messages, we check for the first
        chunk of the first and last message, using the chunk_id function
        """
        first_message = email_batch[0]
        last_message = email_batch[-1]
        first_chunk_id = gmail.chunk_id(first_message, 0)
        last_chunk_id = gmail.chunk_id(last_message, 0)
        return (self._index.fetch(ids=[first_chunk_id])['vectors']
                and self._index.fetch(ids=[last_chunk_id])['vectors'])

    def update_email_index(self, start_date=None, end_date=None):
        """Update the email index with emails between start_date and end_date"""
        email_batches = gmail.email_batches(start_date, end_date)
        while ((email_batch := next(email_batches, None))
               and not(self._already_fully_stored(email_batch))):
            self._store_email_batch(email_batch)

