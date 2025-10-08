from azure.search.documents import SearchClient
from app.settings import get_settings
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

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

settings = get_settings()

#Use default azure credential to get token for Azure OpenAI and Azure AI Search
token_provider = get_bearer_token_provider(DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default")

search_client = SearchClient(
    endpoint = settings.azure_ai_search_endpoint,
    index_name = settings.azure_ai_search_index_name,
    credential = DefaultAzureCredential()
)


def azure_ai_search(query: str, top_k: int = 3):
    """Search documents in Azure AI Search index."""
    print(f"Searching Azure AI Search for query: {query} with top_k={top_k}")
    results = search_client.search(
        search_text=query,
        top=top_k,
        select=["id", "breed_name", "content", "file_name"],
        query_type="semantic", 
        query_language="en-us"
    )
    docs = [doc["content"] for doc in results]
    print(f"Retrieved {len(docs)} documents from Azure AI Search.")
    return {"documents": docs}