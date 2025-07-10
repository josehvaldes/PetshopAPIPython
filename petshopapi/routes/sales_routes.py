from fastapi import APIRouter, File, UploadFile
from typing import Annotated
from petshopapi.loaders import sales_loader
from petshopapi.logger_config  import logger
router = APIRouter()

@router.post("/upload")
async def create_sales_by_file(file: Annotated[bytes, File()]):
    """
    Create sales from a file.
    The file should contain sales data in a specific format.
    """
    logger.info(f"Received file with {len(file)} bytes")
    response = await sales_loader.process_sales_data(file)
    # This is a placeholder for the actual file processing logic
    return {"status": response}