from pathlib import Path

from llama_index.core import (
    SimpleDirectoryReader,
    VectorStoreIndex,
)
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# --------------------------------------------------------
# Project paths
# --------------------------------------------------------
BASE_DIR = Path(__file__).parent
TEST_DIR = BASE_DIR / "test"
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

for document in documents:
    print(
        document.metadata.get("file_name")
    )


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

print("Number of chunks:", len(nodes))

# --------------------------------------------------------
# Embedding model
# --------------------------------------------------------

embed_model = HuggingFaceEmbedding(
    model_name="BAAI/bge-small-en-v1.5"
)

# --------------------------------------------------------
# Test embedding
# --------------------------------------------------------

sample_text = "I forgot my password."

embedding = embed_model.get_text_embedding(
    sample_text
)

print("\n" + "=" * 60)
print("EMBEDDING")
print("=" * 60)

print("Text:", sample_text)
print("Embedding dimension:", len(embedding))
print("First 10 values:", embedding[:10])

# --------------------------------------------------------
# Create vector index
# --------------------------------------------------------

index = VectorStoreIndex(
    nodes,
    embed_model=embed_model,
)


# --------------------------------------------------------
# Create retriever
# --------------------------------------------------------