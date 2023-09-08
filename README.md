# TEST REPO - forked - only for test purposes
Talk to your email

# Install
## Secrets management
Secret keys and credentials are loaded from the 'secrets' directory at the root in the project, named {key}.txt (e.g. dust.txt, pinecone.txt, gmail-credentials.txt) for local usage, or from a dynamodb table (see config.py) for production usage--in which case there should be no secrets directory in the deployment.
