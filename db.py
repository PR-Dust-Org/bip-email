#  create emails vector store on pinecone
import pinecone
from bip import utils

pinecone.init(api_key=utils.get_secret("pinecone"),
              environment="eu-west1-gcp")

pinecone.create_index('emails', dimension=1536,
                      metric='cosine',
                      pods=1,
                      replicas=1,
                      pod_type='p1.x1')
metadata_config = {
    'indexed': ['subject', 'date', 'thread_id']
}
pinecone.create_index('emails', dimension=1536,
                      metric='cosine',
                      pods=1,
                      replicas=1,
                      pod_type='p1.x1',
                      metadata_config=metadata_config)
