from typing import Optional, List

from fastapi import UploadFile
from pydantic import BaseModel
from starlette.responses import FileResponse


class SecretModel(BaseModel):
    text: Optional[str] = None
    expire_time: int = 0


class GetSecretModel(BaseModel):
    text: Optional[str] = None
    files: List[str] = []


class SecretModelResponse(FileResponse):
    text: Optional[str] = None
