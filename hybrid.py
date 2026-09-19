from pathlib import Path

from llama_index.core import (
    SimpleDirectoryReader,
)
from llama_index.core.node_parser import SentenceSplitter
from rank_bm25 import BM25Okapi

# --------------------------------------------------------
# Project paths
# --------------------------------------------------------

BASE_DIR = Path(__file__).parent
TEST_DIR = BASE_DIR / "test"
CHROMA_DIR = BASE_DIR / "chroma_db"


# --------------------------------------------------------
# Load documents
# --------------------------------------------------------

documents = SimpleDirectoryReader(
    input_dir=str(TEST_DIR),
    required_exts=[".txt", ".md"],
).load_data()

print("=" * 60)
print("DOCUMENT INGESTION")
print("=" * 60)
print("Documents loaded:", len(documents))
# --------------------------------------------------------
# Create chunks
# --------------------------------------------------------

splitter = SentenceSplitter(
    chunk_size=300,
    chunk_overlap=50,
)

nodes = splitter.get_nodes_from_documents(
    documents
)


print("\n" + "=" * 60)
print("CHUNKING")
print("=" * 60)

print("Chunks:", len(nodes))



# ---------------------------------------------------------
# Load your chunks
# ---------------------------------------------------------

all_chunks = [
    node.get_content()
    for node in nodes
]


# ---------------------------------------------------------
# Create BM25 index
# ---------------------------------------------------------

tokenized_chunks = [
    chunk.lower().split()
    for chunk in all_chunks
]

bm25 = BM25Okapi(tokenized_chunks)


# ---------------------------------------------------------
# User query
# ---------------------------------------------------------

query = input("Enter your question: ")


# ---------------------------------------------------------
# Keyword search
# ---------------------------------------------------------

query_tokens = query.lower().split()

keyword_scores = bm25.get_scores(
    query_tokens
)


# ---------------------------------------------------------
# Get top keyword results
# ---------------------------------------------------------

top_k = 5

keyword_indexes = sorted(
    range(len(keyword_scores)),
    key=lambda i: keyword_scores[i],
    reverse=True
)[:top_k]


print("\n========== KEYWORD RESULTS ==========\n")

for rank, index in enumerate(keyword_indexes, start=1):

    print(f"Result {rank}")
    print(f"Score: {keyword_scores[index]}")
    print(all_chunks[index])
    print("-" * 60)