from bip import utils
from bip.config import test_email
from bip.email import gmail, retriever    

from numpy import dot
from numpy.linalg import norm


def cosine_similarity(a, b):
    return dot(a, b)/(norm(a)*norm(b))


def show_outputs(gmail_client, message_ids, query):
    # get the message
    messages = [gmail._get_message(gmail_client, {'id': message_id})
                for message_id in message_ids]
    # get the raw text
    chunks = retriever.Retriever(test_email, "chunks1k")._cut_messages(messages)
    query_vector = utils.embed(query)
    # sort by similarity
    chunks = sorted(chunks, key=lambda x: cosine_similarity(query_vector, x[1]), reverse=True)
    for _, v, m in chunks:
        score = cosine_similarity(query_vector, v)
        subject = m['subject']
        index = m['chunk_index']
        print(f"{score} - {subject} - {index}")
        print(m['text'])

    for _, v, m in chunks:
        score = cosine_similarity(query_vector, v)
        subject = m['subject']
        index = m['chunk_index']
        print(f"{score} - {subject} - {index}")


if __name__ == "__main__":
    gmail_client = gmail.gmail_api_client(test_email)
    bruyants_id = "187933238ec01bee"
    gens_conf_id = "1867a83210ef9e30"
    amazon_id = "18703a36a86f6fa4"

    show_outputs(gmail_client, [bruyants_id, gens_conf_id, amazon_id],
                 "achat du livre nos voisins silencieux")
                 # "mail d'amazon")
                 
