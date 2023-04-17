# tests upsert & retrieval in pinecone db
import pinecone
from langchain.embeddings import OpenAIEmbeddings

from bip import utils

# Connect to pinecone
pinecone.init(api_key=utils.get_secret("pinecone"),
              environment="eu-west1-gcp")
test_namespace = "initial-pinecone-test"

# get 2 embeddings
embeddings = OpenAIEmbeddings()
elt1 = embeddings.embed_query(text="Qui veut la peau de mon équipe?")
elt2 = embeddings.embed_query(text="Il est très en retard")

# Insert some data
index = pinecone.Index("bip-email")
index.delete(deleteAll=True, namespace=test_namespace)
index.upsert(vectors=[("elt0", [0.1]*1536)], namespace=test_namespace)
index.upsert(vectors=[("elt1", elt1, {"m_id": "wow"}),
                      ("elt2", elt2, {"m_id": "wow2"})],
             namespace=test_namespace)

# Check it works
query1 = embeddings.embed_query(text="Une personne de mon équipe")
query2 = embeddings.embed_query(text="Elle est à l'heure")
print(index.fetch(ids=["elt0"],
                  namespace=test_namespace)['vectors']['elt0']['values'][:5])
print(index.query(top_k=1, vector=query1, namespace=test_namespace))
print(index.query(top_k=1, vector=query2, namespace=test_namespace))
