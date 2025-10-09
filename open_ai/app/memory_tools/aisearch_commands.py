"""
Azure AI Search command tool for managing and querying the search index.
Prequisites:
- Python 3.8+
- pip install openai azure-search-documents azure-identity
- Azure OpenAI resource with embedding model deployment
- Azure AI Search resource with vector index
- Appropriate environment variables set in .env file or system environment:
    - AZURE_OPENAI_ENDPOINT
    - AZURE_OPENAI_KEY
    - AZURE_OPENAI_VERSION
    - AZURE_OPENAI_EMBEDDED_MODEL
    - AZURE_OPENAI_MODEL_DEPLOYMENT_NAME
    - AZURE_AI_SEARCH_ENDPOINT
    - AZURE_AI_SEARCH_KEY
    - AZURE_AI_SEARCH_INDEX_NAME

Authentication:
- Set up Azure OpenAI and Azure AI Search resources.
- Use DefaultAzureCredential for authentication, ensure your environment is configured for it.

Usage:
    python aisearch_commands.py <command>
Commands:
    delete  - Delete all documents in the index 
    count   - Count all documents in the index
    search  - Search documents by specific properties
    facet   - Search documents and get facets
    vector  - Search documents using vector search
    hybrid  - Search documents using hybrid search (text + vector)

"""
import argparse
from openai import AzureOpenAI
from azure.search.documents import SearchClient
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from collections import defaultdict
from app.settings import get_settings

settings = get_settings()

endpoint = settings.azure_openai_endpoint
model_name = settings.azure_openai_embedded_model #"text-embedding-3-small"
deployment = settings.azure_openai_model_deployment_name #"text-embedding-3-small_POC"
api_version = "2024-02-01"

#Use default azure credential to get token for Azure OpenAI and Azure AI Search
token_provider = get_bearer_token_provider(DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default")

# --- Azure OpenAI setup ---
client = AzureOpenAI(
    api_version = settings.azure_openai_version, 
    azure_endpoint = settings.azure_openai_endpoint,
    azure_ad_token_provider=token_provider
)

search_client = SearchClient(
    endpoint = settings.azure_ai_search_endpoint,
    index_name = settings.azure_ai_search_index_name,
    credential = DefaultAzureCredential()
)


def get_vector_embedding(text):
    """Get embedding for a single text chunk."""
    response = client.embeddings.create(
        model=settings.azure_openai_embedded_model,
        input=[text]
    )
    return response.data[0].embedding


def delete():
    """Delete all documents in the index."""
    print("Deleting a document in the index...")

    result = search_client.delete_documents(
        documents=[{"id": "e588c2a9-7a8b-4b40-a257-197f81b73251"}],
    )
    print(f"Delete result: {result}")
    return result

def count():
    """Count all documents in the index."""
    print("Counting documents in the index...")
    result = search_client.get_document_count()
    print(f"Document count: {result}")
    return result

def search_by_properties():
    """Search documents by specific properties."""
    print("Searching documents in the index...")
    query = "*"
    
    results = search_client.search(
        search_text=query, 
        select=["id", "breed_name", "content", "file_name"],
        filter = "breed_name eq 'BOXER'",
        top=5
        )

    for result in results:
        print(f"Found document: {result}")

def search_facet():
    """Search documents and get facets."""
    print("Searching documents in the index...")
    
    results = search_client.search(
        search_text="boxer temperament", 
        select=["id", "breed_name", "content"],
        facets=["breed_name,count:2"],
        top=5,
        )

    for facet in results.get_facets()["breed_name"]:
        print(f"Found facet: {facet}")


    for result in results:
        print(f"Found document: {result["id"]}, breed_name: {result["breed_name"]}, content: {result["content"][:30]}...")
    
def search_vector():
    """Search documents using vector search."""
    print("Vector search.")
    query = "dogs for rescue operations"
    query_vector = get_vector_embedding(query)
    print(f"Query vector length: {len(query_vector)}")
    results = search_client.search(
        search_text=None,  # leave empty when using pure vector search
        select=["id", "content", "breed_name"],
        top=5,
        vector_queries= [{
            "vector": query_vector,
            "fields": "content_vector",
            "k": 5,
            "weight": 0.5,
            "kind": "vector"
        }]
        )
    
    for result in results:
        print(f"Found document: {result["id"]}, breed_name: {result["breed_name"]}, score: [{result["@search.score"]}] content: {result["content"][:30]}...")
    
    grouped = defaultdict(list)
    for r in results:
        grouped[r["breed_name"]].append(r)

    # Print top chunk from each document
    for doc_id, chunks in grouped.items():
        print(f"📄 Document: {doc_id}")
        print(f"🔹 Top chunk: {chunks[0]['content'][:150]}...\n")


def search_hybrid_query_vector():
    """Search documents using hybrid search (text + vector)."""
    print("Hybrid search")

    query = "dogs for rescue operations"
    query_vector = get_vector_embedding(query)
    print(f"Query vector length: {len(query_vector)}")

    results = search_client.search(
        search_text=query, 
        select=["id", "content", "breed_name"],
        top=5,
        vector_queries= [{
            "vector": query_vector,
            "fields": "content_vector",
            "k": 5,
            "weight": 0.5,
            "kind": "vector"
            }]
        )
    print("results:")
    for result in results:
        print(f"Found document: {result["id"]}, breed_name: {result["breed_name"]}, score: [{result["@search.score"]}] content: {result["content"][:30]}...")


if __name__ == "__main__":
    print("Starting AISearch command tool...")
    
    parser = argparse.ArgumentParser(description="Azure AI Search Command Tool")
    parser.add_argument("command", type=str, help="command to execute: delete, count")
    args = parser.parse_args()
    command = args.command.lower()
    if command == "delete":
        print("Executing delete command...")
        delete()
    elif command == "count":
        print("Executing count command...")
        count()
    elif command == "search":
        print("Executing search command...")
        search_by_properties()
    elif command == "facet":
        print("Executing facet command...")
        search_facet()
    elif command == "vector":
        print("Executing vector search command...")
        search_vector()
    elif command == "hybrid":
        print("Executing hybrid search command...")
        search_hybrid_query_vector()
    else:
        print(f"Unknown command: {command}. Supported commands are: delete, count.")
    print("AISearch command tool completed.")


