# Main bip-email code
import sys

from langchain import OpenAI
from langchain.chains import RetrievalQAWithSourcesChain

from bip.email.gmail import get_last_threads, gmail_api_client
from bip.email.store import store_in_chroma_db, docsearch

if __name__ == '__main__':
    # get user's query from command line
    # query = sys.argv[1]
    query = "Quels nouveaux appartements me sont proposés?"
    # store the last 10 threads from Gmail in chroma
    for thread in get_last_threads(gmail_api_client("../.."), 10):
        store_in_chroma_db(thread)
    chain = RetrievalQAWithSourcesChain.from_chain_type(
        OpenAI(temperature=0, model_name="gpt-4"),
        chain_type="stuff",
        retriever=docsearch.as_retriever())
    print(chain(query))