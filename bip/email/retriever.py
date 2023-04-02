# This module retrieves emails from a gmail account and stores them in a
# vector store
from datetime import datetime
import logging
import os.path
import sys

import pinecone

from langchain.embeddings import OpenAIEmbeddings
from bip.email import gmail, chunker

logging.basicConfig(level=logging.INFO)


def get_pinecone_key(key_dir='secrets'):
    """Get Pinecone API key from secrets/pinecone-key.txt"""
    with open(os.path.join(key_dir,'pinecone-key.txt')) as f:
        return f.read().strip()


class Retriever(object):
    UPSERT_BATCH_SIZE = 100

    def __init__(self, namespace=None, creds_dir='secrets'):
        self._namespace = namespace
        self._gmail_client = gmail.gmail_api_client(creds_dir)
        pinecone.init(api_key=get_pinecone_key(creds_dir),
                      environment="eu-west1-gcp")
        self._index = pinecone.Index("bip-email")
        self._embeddings = OpenAIEmbeddings()
        logging.info("Retriever initialized")

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
        first_chunk_id = chunker.chunk_id(first_message, 0)
        last_chunk_id = chunker.chunk_id(last_message, 0)
        return (self._index.fetch(ids=[first_chunk_id])['vectors']
                and self._index.fetch(ids=[last_chunk_id])['vectors'])

    def _store_chunks(self, chunks):
        for i in range(0, len(chunks), self.UPSERT_BATCH_SIZE):
            logging.info(
                f"Upserting chunks {i} to {i + self.UPSERT_BATCH_SIZE}")
            self._index.upsert(vectors=chunks[i:i + self.UPSERT_BATCH_SIZE],
                               namespace=self._namespace)

    def _cut_messages(self, email_batch):
        """Cut messages into chunks and embed them"""
        chunks = []
        for i, message in enumerate(email_batch):
            if i % 10 == 0:
                logging.info(f"Cutting message {i} of {len(email_batch)}")
            enriched_chunks, metadatas = chunker.cut_message(message)
            chunk_vectors = self._embeddings.embed_documents(enriched_chunks)
            for cv, m in zip(chunk_vectors, metadatas):
                chunk_id = chunker.chunk_id(message, m['chunk_index'])
                chunks.append((chunk_id, cv, m))
        return chunks

    def _log_batch_date(self, email_batch):
        """Log the date of the first message in the batch"""
        first_message_ts = int(email_batch[0]['internalDate']) / 1000
        batch_date = (datetime.fromtimestamp(first_message_ts)
                      .strftime("%Y-%m-%d %H:%M"))
        logging.info(f"Storing new batch starting from date {batch_date}")

    def _store_email_batch(self, email_batch):
        """Store an email batch in the index"""
        self._log_batch_date(email_batch)
        chunks = self._cut_messages(email_batch)
        self._store_chunks(chunks)

    def update_email_index(self, start_date, end_date):
        """Update the email index with emails between start_date and end_date"""
        logging.info(f"Updating email index with emails between {start_date} and {end_date}")
        batches = gmail.email_batches(self._gmail_client, start_date, end_date)
        for email_batch in batches:
            if not(self._already_fully_stored(email_batch)):
                self._store_email_batch(email_batch)


if __name__ == '__main__':
    retriever = Retriever()
    script_start_date = datetime.strptime(sys.argv[1], "%Y-%m-%d")
    script_end_date = datetime.strptime(sys.argv[2], "%Y-%m-%d")
    retriever.update_email_index(script_start_date, script_end_date)
