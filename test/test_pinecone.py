# tests upsert & retrieval in pinecone db
import pinecone
from langchain.embeddings import OpenAIEmbeddings


# Get Pinecone API key from secrets/pinecone-key.txt
def get_pinecone_key():
    with open('../secrets/pinecone-key.txt') as f:
        return f.read().strip()


PINECONE_KEY = get_pinecone_key()

# Connect to pinecone
pinecone.init(api_key=PINECONE_KEY, environment="eu-west1-gcp")

# get 2 embeddings
embeddings = OpenAIEmbeddings()
elt1 = embeddings.embed_query(text="Qui veut la peau de mon équipe?")
elt2 = embeddings.embed_query(text="Il est très en retard")

# Insert some data
index = pinecone.Index("bip-email")
index.upsert(vectors=[("elt0", [0.1]*1536)])
index.upsert(vectors=[("elt1", elt1), ("elt2", elt2)])

# Check it works
query1 = embeddings.embed_query(text="Une personne de mon équipe")
query2 = embeddings.embed_query(text="Elle est à l'heure")
print(index.fetch(ids=["elt0"])['vectors']['elt0']['values'][:5])
print(index.query(top_k=1, vector=query1))
print(index.query(top_k=1, vector=query2))
