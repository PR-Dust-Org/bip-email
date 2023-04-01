# Main bip-email code
import logging
import sys
import pinecone

from langchain import vectorstores
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.embeddings import OpenAIEmbeddings

from bip.email import retriever

if __name__ == '__main__':
    query = sys.argv[1]

    logging.info("Starting Pinecone")
    pinecone.init(
        api_key=retriever.get_pinecone_key(),
        environment="eu-west1-gcp")
    index = pinecone.Index("bip-email")
    embeddings = OpenAIEmbeddings()
    docsearch = vectorstores.Pinecone(
        index, embeddings.embed_query, "text", "test")

    logging.info("Starting chain")
    chain = RetrievalQAWithSourcesChain.from_chain_type(
        ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo"),
        chain_type="map_reduce",
        retriever=docsearch.as_retriever())

    logging.info("Running chain")
    print(chain(query))
