# Lists email chunks similar to a given query

from bip.api import BipAPI
from bip.config import retriever_namespace, test_email

api = BipAPI(test_email, retriever_namespace)

res = api._retriever.query("voisins silencieux", top_k=32, include_metadata=True).get('matches')
for match in res:
    print(f"{match['metadata']['message_id']} - {match['metadata']['chunk_index']} - {match['score']} - {match['metadata']['subject']}")
