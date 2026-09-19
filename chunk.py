from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import (
    HierarchicalNodeParser,
    SemanticSplitterNodeParser,
    SentenceSplitter,
    SentenceWindowNodeParser,
    TokenTextSplitter,
)
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# ============================================================
# Load local document
# ============================================================

documents = SimpleDirectoryReader(
    "test",
    required_exts=[".txt",".md"]
).load_data()

print("Documents loaded:", len(documents))


# ============================================================
# 1. SENTENCE SPLITTER
# ============================================================

print("\n\n============================================================")
print("1. SENTENCE SPLITTER")
print("============================================================")

splitter = SentenceSplitter(
    chunk_size=300,
    chunk_overlap=0
)

nodes = splitter.get_nodes_from_documents(documents)

print("Number of chunks:", len(nodes))

for i, node in enumerate(nodes[:5], start=1):

    print("\n------------------------------")
    print(f"CHUNK {i}")
    print("------------------------------")

    print(node.text)
    print("Length:", len(node.text))


# ============================================================
# 2. TOKEN TEXT SPLITTER
# ============================================================

print("\n\n============================================================")
print("2. TOKEN TEXT SPLITTER")
print("============================================================")

splitter = TokenTextSplitter(
    chunk_size=100,
    chunk_overlap=20,
    separator=" "
)

nodes = splitter.get_nodes_from_documents(documents)

print("Number of chunks:", len(nodes))

for i, node in enumerate(nodes[:5], start=1):

    print("\n------------------------------")
    print(f"CHUNK {i}")
    print("------------------------------")

    print(node.text)
    print("Length:", len(node.text))


# ============================================================
# 3. SENTENCE WINDOW
# ============================================================

print("\n\n============================================================")
print("3. SENTENCE WINDOW")
print("============================================================")

node_parser = SentenceWindowNodeParser.from_defaults(
    window_size=2,
    window_metadata_key="window",
    original_text_metadata_key="original_sentence"
)

nodes = node_parser.get_nodes_from_documents(documents)

print("Number of sentence nodes:", len(nodes))

for i, node in enumerate(nodes[:5], start=1):

    print("\n------------------------------")
    print(f"SENTENCE {i}")
    print("------------------------------")

    print("Original sentence:")
    print(node.text)

    print("\nContext window:")
    print(node.metadata.get("window"))


# ============================================================
# 4. SEMANTIC SPLITTER
# ============================================================

print("\n\n============================================================")
print("4. SEMANTIC SPLITTER")
print("============================================================")


embed_model = HuggingFaceEmbedding(
    model_name="BAAI/bge-small-en-v1.5"
)

splitter = SemanticSplitterNodeParser(
    buffer_size=1,
    breakpoint_percentile_threshold=95,
    embed_model=embed_model
)

nodes = splitter.get_nodes_from_documents(documents)
for i, node in enumerate(nodes[:5], start=1):

    print("\n------------------------------")
    print(f"CHUNK {i}")
    print("------------------------------")

    print(node.text)
    print("Length:", len(node.text))

# ============================================================
# 5. HIERARCHICAL NODE PARSER
# ============================================================

print("\n\n============================================================")
print("5. HIERARCHICAL NODE PARSER")
print("============================================================")

node_parser = HierarchicalNodeParser.from_defaults(
    chunk_sizes=[512, 256, 128]
)

nodes = node_parser.get_nodes_from_documents(documents)

print("Number of hierarchical nodes:", len(nodes))

for i, node in enumerate(nodes[:5], start=1):

    print("\n------------------------------")
    print(f"NODE {i}")
    print("------------------------------")

    print(node.text[:500])

    print("\nMetadata:")
    print(node.metadata)


print("\n\n============================================================")
print("CHUNKING PRACTICAL COMPLETED")
print("============================================================")
