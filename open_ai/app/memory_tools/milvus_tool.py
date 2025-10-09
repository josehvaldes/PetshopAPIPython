#TODO to delete this file if not used later
"""Milvus vector database integration tool."""
milvus_tool = {
    "name": "milvus_search",
    "description": "Searches documents by semantic similarity",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "User question to search in Milvus"},
            "top_k": {"type": "integer", "description": "Number of documents to retrieve"}
        },
        "required": ["query"]
    }
}


def milvus_search(query: str, top_k: int = 3):
    # TODO
    # 1. Embed query using Azure OpenAI embedding model
    # 2. Search Milvus vector DB
    # 3. Return top_k docs

    retrieved_docs =""
    return {"documents": retrieved_docs}

