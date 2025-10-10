"""
Loader for questionnaire blobs.
Stores questionnaire data as blobs in Azure Blob Storage.
The blob name is "{questionnaire_name}/{user_name}.txt".

Requirements:
    pip install azure-storage-blob
"""
import os
import uuid

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from azure.core.exceptions import ResourceNotFoundError
from app.settings import get_settings

settings = get_settings()

def get_blob_container_client() -> ContainerClient:
    """
    Create the container if it doesn't exist and return a ContainerClient.
    """
    blob_service_url = settings.azure_storage_blob_service_url
    container_name: str = settings.azure_storage_blob_container_name
    
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

def upload_questionnaire_blob(container_client:BlobServiceClient, content: dict) -> None:
    """
    Upload a questionnaire blob for the given user and questionnaire IDs.
    The blob name is "{questionnaire_name}/{user_name}.txt".
    """
    blob_name = f"{content["questionnaire"]["questionnaire_name"]}/{content["user_name"]}.txt"
    print(f"Preparing to upload blob: {blob_name}")
    blob_client = container_client.get_blob_client(blob_name)
    
    print(f"Uploading blob: {blob_name}")
    blob_client.upload_blob(str(content), overwrite=True)
    print("Upload complete.")

def main():

    blob_client = get_blob_container_client()

    # Example usage
    print("Uploading a sample questionnaire blob...")
    user_name = "yuna_syushin"
    questionnaire_name = "dog_preferences"
    content = {
        "user_name": user_name,
        "age": "20",
        "gender": "female",
        "questionnaire": {
            "questionnaire_name": questionnaire_name,
            "preferred_size": "small",
            "temperament": "calm",
            "maintainability": "low",
            "exercise_requirement": "low"
            }
        }
    upload_questionnaire_blob(blob_client,content)

    user_name = "john_doe"
    questionnaire_name = "dog_preferences"
    content = {
        "user_name": user_name,
        "age": "15",
        "gender": "male",
        "questionnaire": {
            "questionnaire_name": questionnaire_name,
            "preferred_size": "big",
            "temperament": "energetic",
            "maintainability": "low",
            "exercise_requirement": "high"
            }
    }
    upload_questionnaire_blob(blob_client, content)

    #sample 3
    user_name = "alice_wonder"
    questionnaire_name = "dog_preferences"
    content = {
        "user_name": user_name,
        "age": "10",
        "gender": "female",
        "questionnaire": {
            "questionnaire_name": questionnaire_name,
            "preferred_size": "small",
            "temperament": "gentle",
            "maintainability": "high",
            "exercise_requirement": "low"
            }
    }
    upload_questionnaire_blob(blob_client, content)

    #sample 4
    user_name = "bob_builder"
    questionnaire_name = "dog_preferences"
    content = {
        "user_name": user_name,
        "age": "12",
        "gender": "male",
        "questionnaire": {
            "questionnaire_name": questionnaire_name,
            "preferred_size": "medium",
            "temperament": "friendly",
            "maintainability": "low",
            "exercise_requirement": "medium"
            }
    }
    upload_questionnaire_blob(blob_client, content)

if __name__ == "__main__":
    main()