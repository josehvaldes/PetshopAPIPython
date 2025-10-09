"""
Add rows to an Azure Table Storage table named 'dog_owner_questionnaire'.

Prerequisites:
- Python 3.8+
- pip install azure-data-tables

Authentication:
- update the user_profile_table_url value in the config/config.toml file or set the environment variable:
    export user_profile_table_url="https://{storageaccountname}.table.core.windows.net/{tablename}}"

Entity keys:
- Azure Table Storage requires PartitionKey and RowKey for every entity.
- In this example:
    PartitionKey = user_id
    RowKey       = questionnaire_id
"""

import os
import uuid
from datetime import datetime, timezone
from typing import Dict, Iterable, Optional

from azure.identity import DefaultAzureCredential
from azure.data.tables import TableServiceClient, UpdateMode
from azure.core.exceptions import HttpResponseError

from app.settings import get_settings

settings = get_settings()

def get_table_client() -> TableServiceClient:
    """
    Create the table if it doesn't exist and return a TableClient.
    """
    table_service_url = settings.azure_storage_table_service_url
    table_name: str = settings.azure_storage_table_name
    
    if not table_service_url:
        raise RuntimeError("Missing table URL in config.toml [azure_storage_account] table_service_url")
    if not table_name:
        raise RuntimeError("Missing table name in config.toml [azure_storage_account] table_name")

    print(f"Table service URL: {table_service_url}")
    print(f"Connecting to Azure Table Storage with table: {table_name}")
    service = TableServiceClient(endpoint=table_service_url, credential = DefaultAzureCredential())
    
    # idempotent: creates only if missing
    service.create_table_if_not_exists(table_name=table_name)
    return service.get_table_client(table_name)


def _to_utc(dt: Optional[datetime]) -> datetime:
    """
    Ensure a timezone-aware UTC datetime. If dt is None, returns now in UTC.
    """
    if dt is None:
        return datetime.now(timezone.utc)
    if dt.tzinfo is None:
        # Assume naive = UTC; attach UTC tzinfo
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def build_entity(row: Dict) -> Dict:
    """
    Build a valid Azure Table entity from an input dict with the expected columns.

    Expected input fields:
      - questionnaire_id: str (auto-generated if missing)
      - user_id: str
      - username: str
      - dog_breed: str
      - dog_name: str
      - age: int
      - temperament: str
      - created_on: datetime (optional; defaults to now in UTC)

    Returns a dict that includes PartitionKey and RowKey.
    """
    questionnaire_id = str(row.get("questionnaire_id") or uuid.uuid4())
    user_id = str(row["user_id"])

    entity = {
        # Required keys for Azure Table Storage
        "PartitionKey": user_id,
        "RowKey": questionnaire_id,

        # Your columns (duplicated for convenience/filtering)
        "questionnaire_id": questionnaire_id,
        "user_id": user_id,
        "username": str(row["username"]),
        "dog_breed": str(row["dog_breed"]),
        "dog_name": str(row["dog_name"]),
        "age": int(row["age"]),
        "temperament": str(row["temperament"]),
        "created_on": _to_utc(row.get("created_on")),
    }
    return entity


def upsert_row(table_client, row: Dict) -> None:
    """
    Upsert (insert or merge) a single row.
    """
    entity = build_entity(row)
    table_client.upsert_entity(mode=UpdateMode.MERGE, entity=entity)


def upsert_rows(table_client, rows: Iterable[Dict]) -> None:
    """
    Upsert multiple rows. This implementation loops row-by-row for simplicity.
    For large batches per partition, you can optimize using submit_transaction().
    """
    for row in rows:
        upsert_row(table_client, row)


def main():

    table = get_table_client()

    # Example: add a single row
    single_row = {
        "questionnaire_id": "q-0001",  # optional; if omitted, a UUID will be generated
        "user_id": "user-123",
        "username": "jane.doe",
        "dog_breed": "Border Collie",
        "dog_name": "Skye",
        "age": 4,
        "temperament": "Energetic and intelligent",
        # "created_on": datetime.now(timezone.utc),  # optional
    }

    # Example: add multiple rows
    multiple_rows = [
        {
            "questionnaire_id": "q-0002",
            "user_id": "user-123",
            "username": "jane.doe",
            "dog_breed": "Border Collie",
            "dog_name": "Moss",
            "age": 2,
            "temperament": "Playful",
        },
        {
            # questionnaire_id omitted -> will be auto-generated UUID
            "user_id": "user-789",
            "username": "john.smith",
            "dog_breed": "Labrador Retriever",
            "dog_name": "Buddy",
            "age": 5,
            "temperament": "Friendly",
        },
    ]

    try:
        # Upsert single
        upsert_row(table, single_row)
        print("Inserted/updated single row.")

        # Upsert multiple
        upsert_rows(table, multiple_rows)
        print("Inserted/updated multiple rows.")
    except HttpResponseError as e:
        print(f"Azure Table operation failed: {e}")
        raise


if __name__ == "__main__":
    main()