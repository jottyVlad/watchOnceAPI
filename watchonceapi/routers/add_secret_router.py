import json
from sqlite3 import Cursor
from typing import Annotated, Optional, List, Union

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from minio import Minio
from pydantic import ValidationError

from watchonceapi.dependencies.db import get_db_cursor
from watchonceapi.dependencies.minio import get_minio_client
from watchonceapi.models import SecretModel
from watchonceapi.services.add_secret_service import add_secret_to_db, \
    check_files_and_text_status_or_404, handle_status

add_secret_router = APIRouter()


def checker(data: str = Form(...)):
    try:
        model = SecretModel.model_validate(json.loads(data))
    except ValidationError:
        raise HTTPException(status_code=422)

    return model


@add_secret_router.post("/add", response_model=SecretModel)
async def add_secret(
        cursor: Annotated[Cursor, Depends(get_db_cursor)],
        minio: Annotated[Minio, Depends(get_minio_client)],
        secret: SecretModel = Depends(checker),
        files: List[UploadFile] = File(...)
):
    status = check_files_and_text_status_or_404(secret, files)
    handle_status(status, secret, files, cursor, minio)
    # add_secret_to_db(secret.text,
    #                  secret.expire_time,
    #                  cursor)
    return secret
