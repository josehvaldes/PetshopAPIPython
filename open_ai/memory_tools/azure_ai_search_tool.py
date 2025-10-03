from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

ai_search_tool = {
    "name": "azure_ai_search",
    "description": "Searches documents in Azure AI Search index with hybrid semantic + vector search",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "User question to search in Azure AI Search"},
            "top_k": {"type": "integer", "description": "Number of documents to retrieve"}
        },
        "required": ["query"]
    }
}


search_client = SearchClient(
    endpoint="https://<service-name>.search.windows.net",
    index_name="documents-index",
    credential=AzureKeyCredential("Update key here")
)

def azure_ai_search(query: str, top_k: int = 3):
    results = search_client.search(
        search_text=query,
        top=top_k,
        query_type="semantic",  # uses Azure semantic search (hybrid)
        query_language="en-us"
    )
    docs = [doc["content"] for doc in results]
    return {"documents": docs}