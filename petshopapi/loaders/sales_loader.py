from petshopapi.logger_config  import logger
from petshopapi.config import settings

import pandas as pd
import io
from azure.data.tables import TableClient, TableServiceClient
from azure.identity import DefaultAzureCredential


storate_account_url = settings["settings"]["azure_storage_account_url"]    
table_name = settings["settings"]["azure_table_name"]

def does_table_exist(table_name: str, table_service:TableServiceClient) -> bool:
    """
    Check if the specified table exists in Azure Table Service.
    """
    tables = table_service.list_tables()
    try:
        return any(table.name == table_name for table in tables)
    except Exception as e:
        logger.error(f"Error checking if table exists: {e}")
        return False

async def process_sales_data(file_content: bytes) -> str:
    """
    Process the sales data from the file content.
    This function should contain the logic to parse and process the sales data.
    """
    logger.info(f"Processing {len(file_content)} bytes of sales data.")

    credentials = DefaultAzureCredential()
    table_service_client = TableServiceClient(
        endpoint=storate_account_url, credential=credentials
    )
        
    if does_table_exist(table_name, table_service_client):
        logger.info(f"Connected to Azure Table Service at {storate_account_url}")
        table_client : TableClient = table_service_client.get_table_client(table_name = table_name)
        logger.info(f"Connected to table: {table_name}")
        # Assuming the file content is in CSV format
        # Convert bytes to a BytesIO stream for pandas to read
        bytes_stream = io.BytesIO(file_content)
        df = pd.read_csv(bytes_stream, sep=',', header=0)
        df.rename(columns={"domain":"PartitionKey", "saleid":"RowKey"}, inplace=True)
        
        for index, row in df.iterrows():
            logger.warning(f"Processing row {index}: {row.to_dict()}")
            table_client.create_entity(entity=row.to_dict())
            # Here you would add logic to process each row, e.g., saving to a database
            # Add sales to azure table or any other storage
   
        return "Sales data processed successfully."
    else:
        logger.error(f"Table '{table_name}' does not exist.")
        return f"Table '{table_name}' does not exist."
    
    