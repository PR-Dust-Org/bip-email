from googleapiclient.discovery import build
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma

from bip.email.gmail import get_message_text_from_payload, get_header_value, \
    get_last_threads, credentials

embeddings = OpenAIEmbeddings()
docsearch = Chroma("langchain_store", embeddings)


def _create_chunk_metadata(chunk, message, thread_id):
    """Create metadata for the chunk, with the id of the thread, id of the
    message, date of the message, and chunk position

    :param chunk: the chunk
    :param message: the message
    :param thread_id: the thread id
    :return: the metadata
    """
    subject = get_header_value(message['payload']['headers'], 'Subject')
    date = get_header_value(message['payload']['headers'], 'Date')
    metadata = {
        'subject': subject,
        'message_id': message['id'],
        'date': date,
        'thread_id': thread_id,
        'source': message['snippet'],
    }
    return metadata


def _enrich_chunk(chunk, message, index, total):
    """Add subject, sender, main recipients and date as header text to
    the chunk.

    :param chunk: the chunk to enrich
    :param message: the message to get the headers from
    :return: the enriched chunk
    """
    subject = get_header_value(message['payload']['headers'], 'Subject')
    sender = get_header_value(message['payload']['headers'], 'From')
    date = get_header_value(message['payload']['headers'], 'Date')
    recipients = get_header_value(message['payload']['headers'], 'To')
    enriched_chunk = f"Subject: {subject}\n" \
                     f"From: {sender}\n" \
                     f"To: {recipients}\n" \
                     f"Date: {date}\n" \
                     f"Message part {index} of {total}\n" \
                     f"*******************\n\n" \
                     f"{chunk}"
    return enriched_chunk


def _create_chunks(message, chunk_size=2000):
    """Create chunks from the message.

    :param message: the message to chunk
    :return: the chunks
    """
    message_text = get_message_text_from_payload(message['payload'])
    chunks = []
    for i in range(0, len(message_text), chunk_size):
        chunks.append(message_text[i:i + chunk_size])
    return chunks


def _store_message(message, thread_id):
    """Store the message in the chroma database.

    Cut the message in chunks, enrich them, create the metadata for each chunk
    and store them in the chroma database.
    """
    # compute chunks
    chunks = _create_chunks(message)
    if not chunks:
        print("Warning: empty message")
        return

    # compute enriched chunks
    def enrich_chunk(c,i):
        _enrich_chunk(c, message, i, len(chunks))
    enriched_chunks = list(map(enrich_chunk, chunks, range(1, len(chunks)+1)))

    # compute chunks metadatas
    def chunk_metadata(chunk):
        _create_chunk_metadata(chunk, message, thread_id)
    chunks_metadatas = list(map(chunk_metadata, enriched_chunks))

    # store in chroma database
    docsearch.add_texts(enriched_chunks, chunks_metadatas)
    print("Message stored in chroma database")


def store_in_chroma_db(thread):
    """Store the thread in the chroma database.

    :param thread: the thread to store
    """
    for message in thread['messages']:
        _store_message(message, thread['id'])


def test_chunks():
    gmail_api_client = build('gmail', 'v1', credentials=credentials())

    # Get last threads from gmail, store their content in a chroma database
    for thread in get_last_threads(gmail_api_client, 3):
        chunks = _create_chunks(thread['messages'][0])
        enriched_chunks = list(map(lambda chunk, index: _enrich_chunk(chunk,
                                                                  thread['messages'][0],
                                                                 index, len(chunks)),
                              chunks, range(1, len(chunks)+1)))
        chunks_metadatas = list(map(lambda chunk: _create_chunk_metadata(chunk,
                                                                     thread[
                                                                         'messages'][0], thread['id']), enriched_chunks))
        print("Chunks:" + str(len(chunks)))
        print("Enriched chunks:" + str(len(enriched_chunks)))
        print("Chunks metadatas:" + str(len(chunks_metadatas)))
        for chunk, metadata in zip(enriched_chunks, chunks_metadatas):
            print(chunk)
            print(metadata)
            print("")

if __name__ == '__main__':
    [1, 2, 3]._t(print)