import uuid
from openai import AzureOpenAI
from app.memory_tools.vectorized_file import VectorizedFile
from app.memory_tools.file_parser import get_files_as_dict
from app.memory_tools.aisearch_vector_converter import get_vectorized_files, semantic_text_splitter
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from app.settings import AppSettings, get_settings

settings = get_settings()

# --- Azure OpenAI setup ---
print("Create Azure OpenAI clients")
client = AzureOpenAI(
    api_version = settings.azure_openai_version, 
    azure_endpoint = settings.azure_openai_endpoint,
    api_key = settings.azure_openai_key,
)

print("AzureOpenAI client created")

search_client = SearchClient(
    endpoint = settings.azure_ai_search_endpoint,
    index_name = settings.azure_ai_search_index_name,
    credential = AzureKeyCredential(settings.azure_ai_search_key)
)
print("SearchClient client created")

def embed_texts(texts):
    """Get embeddings for a list of text chunks."""
    print(f"    Embedding {len(texts)} chunks to {settings.azure_openai_embedded_model}...")
    response = client.embeddings.create(
        model=settings.azure_openai_model_deployment_name,
        input=texts
    )
    print(f"    Received {len(response.data)} embeddings.")
    return [d.embedding for d in response.data]

def load_vector(vector_files:list[VectorizedFile]):
    print(f"Embedding and indexing {len(vector_files)} files...")
    
    for vf in vector_files:  # Limit to first file for testing
        if len(vf['texts']) > 0:
            print(f"Embedding file: {vf['file_name']} with {len(vf['texts'])} text chunks.")
            embeddings = embed_texts(vf['texts'])
            vf['vectors'] = embeddings
        else:
            print(f"File: {vf['file_name']} has no texts to embed.")
        
        docs_to_index = []
        print(f"Preparing documents for indexing. Filename: {vf["file_name"]}")
        if len(vf["vectors"])> 0 and len(vf['texts']) > 0 and  len(vf["vectors"]) == len(vf['texts']):
            for vector, text in zip(vf["vectors"], vf["texts"]):
                docs_to_index.append(
                {
                    "id": str(uuid.uuid4()),
                    "breed_name": vf["file_name"],
                    "content": text,                    
                    "content_vector": vector,
                    "file_name": f"{vf["file_name"]}.txt",
                    #** add additional metadata
                })
        search_client.upload_documents(documents=docs_to_index)
        print(f"Completed vector file: {vf['file_name']} indexing. documents indexed: {len(docs_to_index)}")
    
    print("End load_vector")


if __name__ == "__main__":
    print("Starting AISearch data loader...")
    files_dict = get_files_as_dict()
    vector_files = get_vectorized_files(files_dict, semantic_text_splitter)
    load_vector(vector_files)
        

            

        