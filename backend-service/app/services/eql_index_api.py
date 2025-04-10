from fastapi import APIRouter

router = APIRouter()

@router.get("/ping")
def ping_index():
    return {"message": "Index API is alive!"}