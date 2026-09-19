import hashlib
from pathlib import Path

import chromadb
from llama_index.core import (
    SimpleDirectoryReader,
    StorageContext,
    VectorStoreIndex,
)
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore

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


# --------------------------------------------------------
# Create stable IDs for nodes
# --------------------------------------------------------

for node in nodes:

    file_name = node.metadata.get(
        "file_name",
        "unknown"
    )

    chunk_text = node.text

    # Create a stable string
    unique_string = (
        f"{file_name}:{chunk_text}"
    )

    # Create stable hash
    stable_id = hashlib.sha256(
        unique_string.encode("utf-8")
    ).hexdigest()

    # Replace automatically generated node ID
    node.node_id = stable_id


# --------------------------------------------------------
# Embedding model
# --------------------------------------------------------

embed_model = HuggingFaceEmbedding(
    model_name="BAAI/bge-small-en-v1.5"
)


# --------------------------------------------------------
# Create persistent Chroma client
# --------------------------------------------------------

print("\n" + "=" * 60)
print("CHROMA")
print("=" * 60)

chroma_client = chromadb.PersistentClient(
    path=str(CHROMA_DIR)
)

print("Database path:", CHROMA_DIR)


# --------------------------------------------------------
# Create / load collection
# --------------------------------------------------------

chroma_collection = chroma_client.get_or_create_collection(
    name="company_knowledge"
)

print(
    "Collection:",
    chroma_collection.name
)


# --------------------------------------------------------
# Connect Chroma to LlamaIndex
# --------------------------------------------------------

vector_store = ChromaVectorStore(
    chroma_collection=chroma_collection
)

storage_context = StorageContext.from_defaults(
    vector_store=vector_store
)


# --------------------------------------------------------
# Get existing IDs from Chroma
# --------------------------------------------------------

existing_ids = set(
    chroma_collection.get(
        include=[]
    )["ids"]
)

print(
    "Existing vectors:",
    len(existing_ids)
)


# --------------------------------------------------------
# Find only new nodes
# --------------------------------------------------------

new_nodes = []

for node in nodes:

    node_id = node.node_id

    if node_id not in existing_ids:
        new_nodes.append(node)


# --------------------------------------------------------
# Ingest only new nodes
# --------------------------------------------------------

print("\n" + "=" * 60)
print("INCREMENTAL INGESTION")
print("=" * 60)

if new_nodes:

    print(
        f"Found {len(new_nodes)} new nodes."
    )

    print(
        "Creating embeddings and adding them to Chroma..."
    )

    index = VectorStoreIndex(
        new_nodes,
        storage_context=storage_context,
        embed_model=embed_model,
    )

else:

    print("No new documents found.")
    print("Loading existing vector index...")

    index = VectorStoreIndex.from_vector_store(
        vector_store,
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

    "I cannot connect to the company VPN",

    "My laptop is running very slowly",

    "What should I do for VPN-403?",

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

        print(
            "Score:",
            result.score
        )

        print(
            "Source:",
            result.node.metadata.get(
                "file_name"
            )
        )

        print(result.node.text)


# --------------------------------------------------------
# Collection statistics
# --------------------------------------------------------

print("\n" + "=" * 60)
print("CHROMA COLLECTION")
print("=" * 60)

print(
    "Stored vectors:",
    chroma_collection.count()
)