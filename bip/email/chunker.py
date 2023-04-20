import logging

from bip.email.gmail import get_message_text_from_payload, get_header_value, \
    get_last_threads, gmail_api_client
from bip.config import test_email


def _create_chunk_metadata(chunk, message, chunk_index):
    """Create metadata for the chunk, with the id of the thread, id of the
    message, date of the message, and chunk position

    :param chunk: the chunk
    :param message: the message
    :return: the metadata
    """
    subject = get_header_value(message['payload']['headers'], 'Subject')
    date = message['internalDate']
    metadata = {
        'subject': subject,
        'message_id': message['id'],
        'date': date if date else "No date",
        'chunk_index': chunk_index,
        'thread_id': message['threadId'],
        'source': subject,
        'text': chunk,
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
                     f"Message part {index+1} of {total}\n" \
                     f"*******************\n\n" \
                     f"{chunk}"
    return enriched_chunk


def _create_chunks(message, chunk_size=5000):
    """Create chunks from the message.

    :param message: the message to chunk
    :return: the chunks
    """
    message_text = get_message_text_from_payload(message['payload'])
    chunks = []
    chunk_overlap = int(chunk_size / 20)
    chunk_step = chunk_size - chunk_overlap
    for i in range(0, len(message_text), chunk_step):
        chunks.append(message_text[i:i + chunk_step])
    return chunks


def cut_message(message):
    """
    Cut the message in chunks, enrich them, create the metadata for each
    chunk and return the outcome

    Documentation on Message object: https://developers.google.com/gmail/api/v1/reference/users/messages

    :param message: the message to cut
    :return: the enriched chunks and the chunks metadatas
    """
    # compute chunks
    chunks = _create_chunks(message)
    if not chunks:
        logging.warning("Empty message")
        return [], []

    # compute enriched chunks
    def enrich_chunk(c,i):
        return _enrich_chunk(c, message, i, len(chunks))
    enriched_chunks = list(map(enrich_chunk, chunks, range(len(chunks))))

    # compute chunks metadatas
    def chunk_metadata(chunk, index):
        return _create_chunk_metadata(chunk, message, index)
    chunks_metadatas = list(map(chunk_metadata, enriched_chunks, range(len(chunks))))

    return enriched_chunks, chunks_metadatas


def chunk_id(message, chunk_index):
    """
    Compute the chunk id from the message id and the chunk index

    :param message: the message
    :param chunk_index: the chunk index
    :return: the chunk id
    """
    return f"{message['id']}-{chunk_index}"


def test_chunks():
    gmail_api_client = gmail_api_client(test_email)

    # Get last threads from gmail, store their content in a chroma database
    for thread in get_last_threads(gmail_api_client, 3):
        enriched_chunks, chunks_metadatas = cut_message(thread['messages'][0])
        print("Enriched chunks:" + str(len(enriched_chunks)))
        print("Chunks metadatas:" + str(len(chunks_metadatas)))
        for chunk, metadata in zip(enriched_chunks, chunks_metadatas):
            print(chunk)
            print(metadata)
            print("")


if __name__ == '__main__':
    test_chunks()