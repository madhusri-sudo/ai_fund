import os
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from google import genai

from llama_index.core import (
    StorageContext,
    VectorStoreIndex,
)

from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore

from langchain.tools import tool


# =========================================================
# LOAD ENVIRONMENT
# =========================================================

load_dotenv()


# =========================================================
# PROJECT PATHS
# =========================================================

BASE_DIR = Path(__file__).parent

CHROMA_DIR = BASE_DIR / "chroma_db"


# =========================================================
# EMBEDDING MODEL
# =========================================================

embed_model = HuggingFaceEmbedding(
    model_name="BAAI/bge-small-en-v1.5"
)


# =========================================================
# CHROMA VECTOR DATABASE
# =========================================================

chroma_client = chromadb.PersistentClient(
    path=str(CHROMA_DIR)
)

chroma_collection = chroma_client.get_or_create_collection(
    name="company_ops_docs"
)


# =========================================================
# VECTOR STORE
# =========================================================

vector_store = ChromaVectorStore(
    chroma_collection=chroma_collection
)


storage_context = StorageContext.from_defaults(
    vector_store=vector_store
)


# =========================================================
# LOAD EXISTING VECTOR INDEX
# =========================================================

index = VectorStoreIndex.from_vector_store(
    vector_store=vector_store,
    embed_model=embed_model
)


# =========================================================
# CREATE RETRIEVER
# =========================================================

retriever = index.as_retriever(
    similarity_top_k=5
)


# =========================================================
# COMPANY RAG SEARCH TOOL
# =========================================================

@tool
def company_rag_search(query: str) -> str:
    """
    Search the company knowledge base using vector retrieval.

    Use this tool when you need information from the
    company's internal documentation.
    """

    # Retrieve Top-K relevant chunks
    results = retriever.retrieve(query)

    # Store retrieved content
    context = []

    for result in results:

        text = result.node.get_content()

        context.append(text)

    # Return retrieved context
    return "\n\n".join(context)


# =========================================================
# USER QUESTION
# =========================================================

query = input("Enter your question: ")


# =========================================================
# CALL THE TOOL
# =========================================================

context = company_rag_search.invoke(
    {"query": query}
)


# =========================================================
# DISPLAY RETRIEVED CONTEXT
# =========================================================

print("\n========== RETRIEVED CONTEXT ==========\n")

print(context)


# =========================================================
# CREATE PROMPT
# =========================================================

prompt = f"""
You are a helpful company support assistant.

Answer the user's question using only the provided context.

Rules:

- Use only the information available in the context.
- Do not invent information.
- If the answer is not available in the context,
  say that the information is not available.
- Give a clear and concise answer.

Context:
{context}

Question:
{query}

Answer:
"""


# =========================================================
# GEMINI CLIENT
# =========================================================

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


# =========================================================
# GENERATE FINAL ANSWER
# =========================================================

response = client.models.generate_content(
    model="gemini-3.1-flash-lite",
    contents=prompt
)


# =========================================================
# FINAL ANSWER
# =========================================================

print("\n========== FINAL ANSWER ==========\n")

print(response.text)