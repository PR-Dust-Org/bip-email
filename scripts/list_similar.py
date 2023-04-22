# Lists email chunks similar to a given query
import sys

from bip.api import BipAPI
from bip.config import retriever_namespace, test_email

api = BipAPI(test_email, retriever_namespace)


def list_similar(query):
    res = api._retriever.query(query, top_k=32, include_metadata=True).get('matches')
    for match in res:
        print(f"{match['metadata']['message_id']} - {match['metadata']['chunk_index']} - {match['score']} - {match['metadata']['subject']}")
        #    print("\n".join(match['metadata']['text'].split("\n")[:4]))


if __name__ == "__main__":
    list_similar(sys.argv[1])
