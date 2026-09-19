from llama_index.core import SimpleDirectoryReader


documents = SimpleDirectoryReader("data").load_data()

print(f"Documents loaded: {len(documents)}")

from llama_index.core import Document

cleaned_documents = []

for document in documents:
    cleaned_text = " ".join(document.text.split())

    cleaned_documents.append(
        Document(
            text=cleaned_text,
            metadata=document.metadata
        )
    )

documents = cleaned_documents

# 3. Inspect documents
for index, document in enumerate(documents, start=1):

    print("\n==============================")
    print(f"DOCUMENT {index}")
    print("==============================")

    print("Metadata:")
    print(document.metadata)

    print("\nText:")
    print(document.text[:500])