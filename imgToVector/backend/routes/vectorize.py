from fastapi import APIRouter
from fastapi import UploadFile
from fastapi import File
from fastapi.responses import FileResponse

router = APIRouter()

@router.post("/vectorize")
async def vectorize(
    files: list[UploadFile] = File(...)
):
    pass