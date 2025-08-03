import os
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableMap

# Load .env and API key
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# Initialize Embeddings
EMBEDDINGS = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key=api_key
)

# Load and split PDF into chunks
def load_and_chunk(file_path):
    loader = PyPDFLoader(file_path)
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    return splitter.split_documents(docs)

# Build FAISS vector store
def build_vectorstore(chunks):
    return FAISS.from_documents(chunks, EMBEDDINGS)

# Define RAG pipeline
def get_rag_chain(vectorstore: FAISS):
    # Simple retriever (no MMR, no compression)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

    # Prompt template with direct answer
    prompt = ChatPromptTemplate.from_template("""
You are a helpful assistant for answering queries about insurance policies.

Use the following context to answer the user's question.
If the answer is not found, say you don’t have enough information.

Context:
{context}

Question: {question}
""")

    # LLM model
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-pro",
        temperature=0,
        google_api_key=api_key
    )

    # Build RAG chain
    chain = (
        RunnableMap({
            "context": lambda x: retriever.invoke(x["question"]),
            "question": lambda x: x["question"]
        })
        | prompt
        | llm
    )

    return chain
