import os
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader

pdf_directory = './documents'
loaders = [PyPDFLoader(os.path.join(pdf_directory, file)) for file in os.listdir(pdf_directory) if file.endswith('.pdf')]

docs = []

for file in loaders:
    docs.extend(file.load())

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
docs = text_splitter.split_documents(docs)

embedding_function = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2", model_kwargs={'device': 'cpu'})

persist_directory = "./chroma_db_nccn"
if os.path.exists(persist_directory):
    vectorstore = Chroma(persist_directory=persist_directory, embedding_function=embedding_function)
else:
    vectorstore = Chroma.from_documents(docs, embedding_function, persist_directory=persist_directory)

vectorstore.add_documents(docs)

print(vectorstore._collection.count())
