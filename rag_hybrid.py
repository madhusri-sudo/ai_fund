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
from rank_bm25 import BM25Okapi

load_dotenv()


# =========================================================
# Project paths
# =========================================================

BASE_DIR = Path(__file__).parent

CHROMA_DIR = BASE_DIR / "chroma_db"


# =========================================================
# Embedding model
# =========================================================

embed_model = HuggingFaceEmbedding(
    model_name="BAAI/bge-small-en-v1.5"
)


# =========================================================
# Chroma
# =========================================================

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


# =========================================================
# Load existing vector index
# =========================================================

index = VectorStoreIndex.from_vector_store(
    vector_store=vector_store,
    embed_model=embed_model
)


# =========================================================
# Create vector retriever
# =========================================================

retriever = index.as_retriever(
    similarity_top_k=5
)


# =========================================================
# User question
# =========================================================

query = input("Enter your question: ")


# =========================================================
# 1. VECTOR SEARCH
# =========================================================

vector_results = retriever.retrieve(query)


print("\n========== VECTOR SEARCH RESULTS ==========\n")

for rank, node in enumerate(vector_results, start=1):

    print(f"Result {rank}")
    print(f"Vector Score: {node.score}")
    print(node.get_content())
    print("-" * 60)


# =========================================================
# 2. GET ALL CHUNKS FOR BM25
# =========================================================
#
# IMPORTANT:
# BM25 should search the complete set of chunks,
# not only the chunks returned by vector search.
#
# For this classroom example, we retrieve all stored
# Chroma documents and build a BM25 index over them.
# =========================================================

all_data = chroma_collection.get(
    include=["documents"]
)

all_chunks = all_data["documents"]


print(f"\nTotal chunks available for BM25: {len(all_chunks)}")


# =========================================================
# 3. CREATE BM25 INDEX
# =========================================================

tokenized_chunks = [
    chunk.lower().split()
    for chunk in all_chunks
]

bm25 = BM25Okapi(tokenized_chunks)


# =========================================================
# 4. KEYWORD SEARCH
# =========================================================

query_tokens = query.lower().split()

keyword_scores = bm25.get_scores(
    query_tokens
)


# =========================================================
# 5. GET TOP-K KEYWORD RESULTS
# =========================================================

top_k = 5

keyword_indexes = sorted(
    range(len(keyword_scores)),
    key=lambda i: keyword_scores[i],
    reverse=True
)[:top_k]


keyword_results = [
    all_chunks[index]
    for index in keyword_indexes
]


print("\n========== KEYWORD SEARCH RESULTS ==========\n")

for rank, index in enumerate(keyword_indexes, start=1):

    print(f"Result {rank}")
    print(f"BM25 Score: {keyword_scores[index]}")
    print(all_chunks[index])
    print("-" * 60)


# =========================================================
# 6. RECIPROCAL RANK FUSION
# =========================================================
#
# We do NOT directly add vector scores and BM25 scores
# because they are on different scales.
#
# Instead, we combine the rankings.
# =========================================================

def reciprocal_rank_fusion(
    result_lists,
    k=60
):
    """
    Combine multiple ranked result lists using RRF.

    result_lists:
        List of ranked document lists.

    k:
        RRF constant used to reduce the impact
        of very high rankings.
    """

    scores = {}

    for results in result_lists:

        for rank, document in enumerate(
            results,
            start=1
        ):

            scores[document] = (
                scores.get(document, 0)
                + 1 / (k + rank)
            )

    ranked_results = sorted(
        scores.items(),
        key=lambda x: x[1],
        reverse=True
    )

    return ranked_results


# =========================================================
# 7. COMBINE VECTOR + KEYWORD RESULTS
# =========================================================

vector_chunks = [
    node.get_content()
    for node in vector_results
]


hybrid_results = reciprocal_rank_fusion(
    [
        vector_chunks,
        keyword_results
    ]
)


# =========================================================
# 8. DISPLAY HYBRID RESULTS
# =========================================================

print("\n========== HYBRID SEARCH RESULTS ==========\n")

for rank, (chunk, score) in enumerate(
    hybrid_results[:top_k],
    start=1
):

    print(f"Result {rank}")
    print(f"RRF Score: {score}")
    print(chunk)
    print("-" * 60)


# =========================================================
# 9. BUILD CONTEXT FROM HYBRID RESULTS
# =========================================================

hybrid_chunks = [
    chunk
    for chunk, score in hybrid_results[:top_k]
]


context = "\n\n".join(
    hybrid_chunks
)


# =========================================================
# 10. CREATE PROMPT
# =========================================================

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


# =========================================================
# 11. GEMINI CLIENT
# =========================================================

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


# =========================================================
# 12. GENERATE FINAL ANSWER
# =========================================================

response = client.models.generate_content(
    model="gemini-3.1-flash-lite",
    contents=prompt
)


# =========================================================
# 13. FINAL ANSWER
# =========================================================

print("\n========== FINAL ANSWER ==========\n")

print(response.text)
