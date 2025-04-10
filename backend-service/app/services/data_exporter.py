from fastapi import APIRouter

router = APIRouter()

@router.get("/ping")
def ping_export():
    return {"message": "Exporter API is alive!"}