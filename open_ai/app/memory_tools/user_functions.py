"""
User-defined functions for the agent to call.
Requirements:
    pip install azure-storage-blob

Functions:
    - get_user_info(user_name: str) -> str    
"""
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, ContainerClient
from typing import Any, Callable, Set

def get_blob_container_client(container_name:str, blob_service_url:str) -> ContainerClient:
    """
    Create the container if it doesn't exist and return a ContainerClient.
    """
   
    if not blob_service_url:
        raise RuntimeError("Missing blob service URL in config.toml [azure_storage_account] blob_service_url")
    if not container_name:
        raise RuntimeError("Missing container name in config.toml [azure_storage_account] blob_container_name")

    print(f"Blob service URL: {blob_service_url}")
    print(f"Connecting to Azure Blob Storage with container: {container_name}")
    service = BlobServiceClient(account_url=blob_service_url, credential=DefaultAzureCredential())
    
    # idempotent: creates only if missing
    if not service.get_container_client(container_name).exists():
        print(f"Container '{container_name}' does not exist. Creating it.")
        service.create_container(name=container_name)

    return service.get_container_client(container_name)


def get_user_info(user_name:str) -> str:
    """
        Retrieve user information from Azure Blob Storage based on user_name.
        The blob name is "{questionnaire_name}/{user_name}.txt".

        :param user_name: The name of the user to retrieve information for.
        :rtype: str
        
        :return: User information as a string. If not found, returns a message indicating no information found.
        :rtype: str
    """
    blob_service_url = "https://.blob.core.windows.net/"
    container_name: str = "userquestionnaires"
    questionnaire_name: str = "dog_preferences"

    container_client = get_blob_container_client(container_name=container_name, blob_service_url=blob_service_url)

    blob_name = f"{questionnaire_name}/{user_name}.txt"
    print(f"Fetching blob for user: {user_name}, blob name: {blob_name}")

    try:
        blob_client = container_client.get_blob_client(blob_name)
        download_stream = blob_client.download_blob()
        content = download_stream.readall()
        return content.decode('utf-8')
    except Exception as e:
        print(f"Error fetching blob for user '{user_name}': {e}")
        return f"No information found for user '{user_name}'."
    


user_functions: Set[Callable[..., Any]] = {
    get_user_info
}

# if __name__ == "__main__":
#     # Example usage
#     user_name = "yuna_syushin"
#     print(f"Fetching info for user: {user_name}")
#     info = get_user_info(user_name)
#     print(f"User info: {info}")
