from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQAWithSourcesChain
from langchain import OpenAI
import os

def add_docs_to_index(docs, index):
    for doc in docs:
        with open(doc) as f:
            data = f.read()
        text_splitter = CharacterTextSplitter(chunk_size=1000,
                                              chunk_overlap=0)
        texts = text_splitter.split_text(data)
        index.add_texts(texts, metadatas=[{"source": f"{doc}-{i}"} for i in
                                          range(len(texts))])

embeddings = OpenAIEmbeddings()
docsearch = Chroma("langchain_store", embeddings)

data_dir = "/home/filou/drafts/orga"
file_names = os.listdir(data_dir)
# filter out files starting with . or ending with ~
file_names = [file_name for file_name in file_names if not file_name.startswith(".") and not file_name.endswith("~")]

print([os.path.join(data_dir, file_name) for file_name in file_names])
add_docs_to_index([os.path.join(data_dir, file_name) for file_name in file_names], docsearch)

chain = RetrievalQAWithSourcesChain.from_chain_type(
    OpenAI(temperature=0),
    chain_type="stuff",
    retriever=docsearch.as_retriever())

print(chain("Que faire si urgence sur un projet?"))