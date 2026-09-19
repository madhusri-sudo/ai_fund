from llama_index.core import SimpleDirectoryReader

documents = SimpleDirectoryReader(
    "data"
).load_data()


print("Number of documents:", len(documents))

for document in documents:
    print("\n------------------------")
    print(document)


for document in documents:
    print("\n------------------------")
    print("Metadata:")
    print(document.metadata)

    print("Text:")
    print(document.text)

for document in documents:
    document.metadata["department"] = "IT"

    print("\n------------------------")
    print("Metadata:")
    print(document.metadata)

    print("Text:")
    print(document.text)