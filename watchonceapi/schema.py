import datetime
from typing import Optional, List

from fastapi import UploadFile
from pydantic import BaseModel


class SecretSchema(BaseModel):
    text: Optional[str] = None
    expire_time: int = 0


class SecretDTO(BaseModel):
    uuid_: str
    text: Optional[str] = None
    expire_time: int = 0
    files: List[UploadFile] = []


class ResponseSecretSchema(BaseModel):
    text: Optional[str] = None
    files: List[str] = []
    expires_at: datetime.datetime
