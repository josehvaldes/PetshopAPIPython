from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def list_users():
    print("Listing sales")
    return [{"TODO": "ADD more functionality"}]
