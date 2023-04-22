# Compare similarity of query "voisins silencieux" with two emails
# - the amazon one, that should be very similar (contains the exact text)
# - one regarding "Passage VMC" that should be less similar

from bip import utils
from bip.email.retriever import Retriever
from bip.config import test_email, retriever_namespace

amazon_chunk_id = '18703a36a86f6fa4-1'
vmc_chunk_id = '18636f0f0a8aded1-1'

# fetch the vectors from pinecone
retriever = Retriever(test_email, retriever_namespace)
amazon_vector = retriever._index.fetch([amazon_chunk_id], retriever_namespace)['vectors'][amazon_chunk_id]['values']
vmc_vector = retriever._index.fetch([vmc_chunk_id], retriever_namespace)['vectors'][vmc_chunk_id]['values']

# get the query vector
query_vector = utils.embed("voisins silencieux")[0]

# compute cosine similarity
from numpy import dot
from numpy.linalg import norm
def cosine_similarity(a, b):
    return dot(a, b)/(norm(a)*norm(b))

print("Cosine similarity with amazon email:", cosine_similarity(query_vector, amazon_vector))
print("Cosine similarity with vmc email:", cosine_similarity(query_vector, vmc_vector))

# also print dot product to see the difference
print("Dot product with amazon email:", dot(query_vector, amazon_vector))
print("Dot product with vmc email:", dot(query_vector, vmc_vector))

# and euclidean distance
def euclidean_distance(a, b):
    return norm(list(map(lambda x: x[0]-x[1], zip(a, b))))

print("Euclidean distance with amazon email:", euclidean_distance(query_vector, amazon_vector))
print("Euclidean distance with vmc email:", euclidean_distance(query_vector, vmc_vector))
