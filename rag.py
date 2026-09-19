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

load_dotenv()


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

BASE_DIR = Path(__file__).parent

CHROMA_DIR = BASE_DIR / "chroma_db"


# ---------------------------------------------------------
# Embedding model
# ---------------------------------------------------------

embed_model = HuggingFaceEmbedding(
    model_name="BAAI/bge-small-en-v1.5"
)


# ---------------------------------------------------------
# Chroma
# ---------------------------------------------------------

chroma_client = chromadb.PersistentClient(
    path=str(CHROMA_DIR)
)

chroma_collection = chroma_client.get_or_create_collection(
    name="company_knowledge"
)

vector_store = ChromaVectorStore(
    chroma_collection=chroma_collection
)

storage_context = StorageContext.from_defaults(
    vector_store=vector_store
)


# ---------------------------------------------------------
# Load existing vector index
# ---------------------------------------------------------

index = VectorStoreIndex.from_vector_store(
    vector_store=vector_store,
    embed_model=embed_model
)


# ---------------------------------------------------------
# Create retriever
# ---------------------------------------------------------

retriever = index.as_retriever(
    similarity_top_k=5
)


# ---------------------------------------------------------
# User question
# ---------------------------------------------------------

query = input("Enter your question: ")


# ---------------------------------------------------------
# Retrieve Top-K chunks
# ---------------------------------------------------------

retrieved_nodes = retriever.retrieve(query)


# ---------------------------------------------------------
# Display retrieved chunks
# ---------------------------------------------------------

print("\n========== RETRIEVED CHUNKS ==========\n")

for i, node in enumerate(retrieved_nodes, start=1):

    print(f"Chunk {i}")
    print(f"Score: {node.score}")
    print(node.get_content())
    print("-" * 60)


# ---------------------------------------------------------
# Build context
# ---------------------------------------------------------

context = "\n\n".join(
    node.get_content()
    for node in retrieved_nodes
)


# ---------------------------------------------------------
# Create prompt
# ---------------------------------------------------------

prompt = f"""
You are a helpful company support assistant.

Answer the user's question using only the provided context.

If the answer is not available in the context,
say that the information is not available.

Context:
{context}

Question:
{query}

Answer:
"""


# ---------------------------------------------------------
# Gemini client
# ---------------------------------------------------------

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


# ---------------------------------------------------------
# Generate final answer
# ---------------------------------------------------------

response = client.models.generate_content(
    model="gemini-3.1-flash-lite",
    contents=prompt
)


# ---------------------------------------------------------
# Final answer
# ---------------------------------------------------------

print("\n========== FINAL ANSWER ==========\n")

print(response.text)