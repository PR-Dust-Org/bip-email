# tests upsert & retrieval in pinecone db
import pinecone
from langchain.embeddings import OpenAIEmbeddings

from bip.email import retriever

# Connect to pinecone
pinecone.init(api_key=retriever.get_pinecone_key(), environment="eu-west1-gcp")

# get 2 embeddings
embeddings = OpenAIEmbeddings()
elt1 = embeddings.embed_query(text="Qui veut la peau de mon équipe?")
elt2 = embeddings.embed_query(text="Il est très en retard")

# Insert some data
index = pinecone.Index("bip-email")
index.upsert(vectors=[("elt0", [0.1]*1536)])
index.upsert(vectors=[("elt1", elt1, { "m_id": "wow"}),
                      ("elt2", elt2, { "m_id": "wow2"})])

# Check it works
query1 = embeddings.embed_query(text="Une personne de mon équipe")
query2 = embeddings.embed_query(text="Elle est à l'heure")
print(index.fetch(ids=["elt0"])['vectors']['elt0']['values'][:5])
print(index.query(top_k=1, vector=query1))
print(index.query(top_k=1, vector=query2))
