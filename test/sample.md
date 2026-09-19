# JSON Parsing with LlamaIndex

This practical shows how to read a local JSON file and convert its content into LlamaIndex documents.

## Files

```text
testrag/
├── sample.json
├── json_parser.py
└── README.md
```

## Install

```bash
pip install llama-index
```

## Example

The `sample.json` file contains property information:

```json
[
  {
    "id": 101,
    "address": "100 Main Street",
    "city": "Toronto",
    "price": 850000
  },
  {
    "id": 102,
    "address": "25 King Street",
    "city": "Mississauga",
    "price": 720000
  }
]
```

## Concept

The JSON file is read and each record can be converted into a separate LlamaIndex `Document`.

```text
sample.json
     ↓
Read JSON
     ↓
Extract records
     ↓
LlamaIndex Documents
     ↓
Nodes
     ↓
Embeddings / Vector Database
```

## Key Point

JSON data is structured data. Unlike normal text documents, we may want to preserve the structure of individual records.

For example:

```text
Property 101 → One document
Property 102 → One document
```

This can make retrieval more meaningful when each JSON object represents an independent entity.
