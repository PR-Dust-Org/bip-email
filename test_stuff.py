# Main bip-email code
import json
import logging
import sys

import pinecone
from langchain import vectorstores
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings

from bip.email import retriever


def use_chain():
    logging.info("Starting chain")
    chain = ConversationalRetrievalChain.from_llm(
        llm=ChatOpenAI(temperature=0, model_name="gpt-4"),
        retriever=docsearch.as_retriever(),
        chain_type="stuff")
    logging.info("Running chain")
    print(chain({'chat_history': {}, 'question': query}))


if __name__ == '__main__':
    query = sys.argv[1]

    logging.info("Starting Pinecone")
    pinecone.init(
        api_key=retriever.get_secret_key("pinecone"),
        environment="eu-west1-gcp")
    index = pinecone.Index("bip-email")
    embeddings = OpenAIEmbeddings()
    docsearch = vectorstores.Pinecone(
        index, embeddings.embed_query, "text")

    results = index.query(vector=embeddings.embed_query(query), top_k=5, include_metadata=True)['matches']
    output = {'texts': [result['metadata']['text'] for result in results],
              'query': query}
    # Array of texts (the text field in the metadata)

    # Write output in JSON format in a file
    with open('output.jsonl', 'w') as f:
        json.dump(output, f)

    # Get a json string from output
    json_string = json.dumps(output)
    # parse the json string and count the number of texts
    json_object = json.loads(json_string)
    print(len(json_object['texts']))