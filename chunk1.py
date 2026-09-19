from pathlib import Path

from llama_index.core import Document, SimpleDirectoryReader
from llama_index.core.node_parser import (
    HTMLNodeParser,
    JSONNodeParser,
    MarkdownNodeParser,
    SentenceSplitter,
    SimpleFileNodeParser,
)

# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).parent

TEST_DIR = BASE_DIR / "test"
HTML_FILE = BASE_DIR / "sample.html"
JSON_FILE = BASE_DIR / "sample.json"


print("Base directory:", BASE_DIR)
print("Test directory:", TEST_DIR)


# ============================================================
# 1. SIMPLE FILE PARSER
# ============================================================

print("\n" + "=" * 50)
print("1. SIMPLE FILE PARSER")
print("=" * 50)

documents = SimpleDirectoryReader(
    str(TEST_DIR)
).load_data()

parser = SimpleFileNodeParser()

nodes = parser.get_nodes_from_documents(documents)

print("Number of nodes:", len(nodes))

for i, node in enumerate(nodes[:3], start=1):

    print(f"\n--- Node {i} ---")
    print(node.text[:300])


# ============================================================
# 2. HTML PARSER
# ============================================================

print("\n" + "=" * 50)
print("2. HTML PARSER")
print("=" * 50)

html_text = HTML_FILE.read_text(
    encoding="utf-8"
)

document = Document(
    text=html_text,
    metadata={
        "file_name": HTML_FILE.name
    }
)

parser = HTMLNodeParser(
    tags=["h1", "h2", "p"]
)

nodes = parser.get_nodes_from_documents(
    [document]
)

print("Number of nodes:", len(nodes))

for i, node in enumerate(nodes[:5], start=1):

    print(f"\n--- Node {i} ---")
    print(node.text)


# ============================================================
# 3. JSON PARSER
# ============================================================

print("\n" + "=" * 50)
print("3. JSON PARSER")
print("=" * 50)

json_text = JSON_FILE.read_text(
    encoding="utf-8"
)

document = Document(
    text=json_text,
    metadata={
        "file_name": JSON_FILE.name
    }
)

parser = JSONNodeParser()

nodes = parser.get_nodes_from_documents(
    [document]
)

print("Number of nodes:", len(nodes))

for i, node in enumerate(nodes[:5], start=1):

    print(f"\n--- Node {i} ---")
    print(node.text)


# ============================================================
# 4. MARKDOWN PARSER
# ============================================================

print("\n" + "=" * 50)
print("4. MARKDOWN PARSER")
print("=" * 50)

md_docs =  SimpleDirectoryReader("test").load_data()
parser = MarkdownNodeParser()

nodes = parser.get_nodes_from_documents(md_docs)
for i, node in enumerate(nodes, start=1):
    print(f"\n--- Node {i} ---")
    print(node.text)

# ============================================================
# 5. SENTENCE SPLITTER
# ============================================================

print("\n" + "=" * 50)
print("5. SENTENCE SPLITTER")
print("=" * 50)

documents = SimpleDirectoryReader(
    str(TEST_DIR),
    required_exts=[".txt"]
).load_data()

splitter = SentenceSplitter(
    chunk_size=300,
    chunk_overlap=50
)

nodes = splitter.get_nodes_from_documents(
    documents
)

print("Number of chunks:", len(nodes))

for i, node in enumerate(nodes[:5], start=1):

    print(f"\n--- Chunk {i} ---")
    print(node.text)
    print("Length:", len(node.text))


# ============================================================
# DONE
# ============================================================

print("\n" + "=" * 50)
print("ALL PARSERS COMPLETED")
print("=" * 50)