#  create emails vector store on pinecone
import pinecone
from bip import utils

pinecone.init(api_key=utils.get_secret("pinecone"),
              environment="eu-west1-gcp")

metadata_config = {
    'indexed': ['subject', 'date', 'thread_id', 'message_id']
}
pinecone.create_index('emails-euclidean', dimension=1536,
                      metric='euclidean',
                      pods=1,
                      replicas=1,
                      pod_type='p1.x1',
                      metadata_config=metadata_config)
