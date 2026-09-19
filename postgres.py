import os
from pathlib import Path
from llama_index.core import (
SimpleDirectoryReader,
StorageContext,
VectorStoreIndex,
)
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.postgres import PGVectorStore

# --------------------------------------------------------
# Project paths
# --------------------------------------------------------

BASE_DIR = Path(__file__).parent
TEST_DIR = BASE_DIR / "test"

# --------------------------------------------------------
# PostgreSQL configuration
# --------------------------------------------------------

DB_NAME = os.getenv(
    "POSTGRES_DB",
    "ragdb",
)

DB_USER = os.getenv(
    "POSTGRES_USER",
    "postgres",
)

DB_PASSWORD = os.getenv(
    "POSTGRES_PASSWORD",
    "postgres",
)

DB_HOST = os.getenv(
    "POSTGRES_HOST",
    "localhost",
)

DB_PORT = int(
    os.getenv(
        "POSTGRES_PORT",
        "5432",
    )
)

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

print("Documents:", len(documents))

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

# --------------------------------------------------------
# Embedding model
# --------------------------------------------------------

embed_model = HuggingFaceEmbedding(
    model_name="BAAI/bge-small-en-v1.5"
)

# --------------------------------------------------------
# PostgreSQL vector store
# --------------------------------------------------------

print("\n" + "=" * 60)
print("POSTGRESQL + PGVECTOR")
print("=" * 60)

vector_store = PGVectorStore.from_params(
    database=DB_NAME,
    host=DB_HOST,
    password=DB_PASSWORD,
    port=DB_PORT,
    user=DB_USER,
    table_name="company_knowledge",
    embed_dim=384,
)

# --------------------------------------------------------
# Storage context
# --------------------------------------------------------

storage_context = StorageContext.from_defaults(
    vector_store=vector_store
)

# --------------------------------------------------------
# Create index
# --------------------------------------------------------

index = VectorStoreIndex(
    nodes,
    storage_context=storage_context,
    embed_model=embed_model,
)

# --------------------------------------------------------
# Create retriever
# --------------------------------------------------------

retriever = index.as_retriever(
    similarity_top_k=3
)

# --------------------------------------------------------
# Queries
# --------------------------------------------------------

queries = [
"I forgot my password",
"My VPN is not connecting",
"My laptop is running slowly",
"What should I do when I see VPN-403?",
]

# --------------------------------------------------------
# Retrieval
# --------------------------------------------------------

for query in queries:
    print("\n" + "=" * 60)
    print("QUERY")
    print("=" * 60)

    print("Question:", query)

    results = retriever.retrieve(query)

    for i, result in enumerate(results):
        print(f"\nResult {i + 1}")
        print("-" * 40)
        print("Score:", result.score)
        print(
            "Source:",
            result.node.metadata.get("file_name")
        )

        print(result.node.text)