# # Simple File
# from llama_index.core.node_parser import SimpleFileNodeParser
# from llama_index.core import SimpleDirectoryReader

# md_docs =  SimpleDirectoryReader("data").load_data()

# parser = SimpleFileNodeParser()

# # Additionally, you can augment this with a text-based parser to accurately handle text length
# md_nodes = parser.get_nodes_from_documents(md_docs)

# for index, document in enumerate(md_nodes, start=1):

#     print("\n==============================")
#     print(f"DOCUMENT {index}")
#     print("==============================")

#     print("Metadata:")
#     print(document.metadata)

#     print("\nText:")
#     print(document.text[:500])


#  HTML

# from pathlib import Path

# from llama_index.core import Document
# from llama_index.core.node_parser import HTMLNodeParser


# # Path to the local HTML file
# html_file = Path("sample.html")


# # Read HTML file
# html_doc = html_file.read_text(encoding="utf-8")

# print("HTML file loaded successfully")


# # Create LlamaIndex Document
# document = Document(
#     id_=str(html_file),
#     text=html_doc
# )


# # Create HTML parser
# parser = HTMLNodeParser(
#     tags=["p", "h1", "h2"]
# )


# # Parse HTML into nodes
# nodes = parser.get_nodes_from_documents([document])


# # Display the nodes
# print(f"\nNumber of nodes: {len(nodes)}")

# for i, node in enumerate(nodes, start=1):
#     print(f"\n--- Node {i} ---")
#     print(node)

# # JSON
# from pathlib import Path

# from llama_index.core import Document
# from llama_index.core.node_parser import JSONNodeParser


# # Read local JSON file
# json_file = Path("sample.json")

# json_text = json_file.read_text(encoding="utf-8")

# print("JSON file loaded successfully")


# # Create LlamaIndex Document
# document = Document(
#     id_=str(json_file),
#     text=json_text
# )


# # Create JSON parser
# parser = JSONNodeParser()


# # Parse JSON into nodes
# nodes = parser.get_nodes_from_documents([document])


# # Display the nodes
# print(f"\nNumber of nodes: {len(nodes)}")

# print(nodes)

# for i, node in enumerate(nodes, start=1):
#     print(f"\n--- Node {i} ---")
#     print(node.text)

# # Markdown
# from llama_index.core.node_parser import MarkdownNodeParser
# from llama_index.core import SimpleDirectoryReader

# md_docs =  SimpleDirectoryReader("test").load_data()
# parser = MarkdownNodeParser()

# nodes = parser.get_nodes_from_documents(md_docs)
# for i, node in enumerate(nodes, start=1):
#     print(f"\n--- Node {i} ---")
#     print(node.text)

# sentence splitting
from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter

documents = SimpleDirectoryReader("test",  required_exts=[".txt"]).load_data()

splitter = SentenceSplitter(
    chunk_size=300,
    chunk_overlap=50
)

nodes = splitter.get_nodes_from_documents(documents)

print("Number of chunks:", len(nodes))

for i, node in enumerate(nodes[:5]):
    print("\n==============================")
    print(f"CHUNK {i + 1}")
    print("==============================")
    print(node.text)
    print("Length:", len(node.text))