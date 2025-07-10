from typing import Union
from pydantic import BaseModel
from fastapi import APIRouter

class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None


router = APIRouter()

@router.get("/{item_id}")
async def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
    
  
