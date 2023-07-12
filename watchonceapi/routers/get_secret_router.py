from sqlite3 import Cursor
from typing import Annotated

from fastapi import APIRouter, Depends
from minio import Minio

from watchonceapi.dependencies.db import get_db_cursor
from watchonceapi.dependencies.minio import get_minio_client
from watchonceapi.models import SecretModelResponse
from watchonceapi.services.get_secret_service import get_secret_or_404, exception404_if_expired
from watchonceapi.services.remove_secret_service import remove_secret_from_db

get_secret_router = APIRouter()


@get_secret_router.get("/get/{secret_id}", response_model=SecretModelResponse)
async def get_secret(
        secret_id: str,
        cursor: Annotated[Cursor, Depends(get_db_cursor)],
        minio: Annotated[Minio, Depends(get_minio_client)]
):
    pass
    # secret = get_secret_or_404(secret_id, cursor, minio)
    # remove_secret_from_db(secret_id, cursor)
    # exception404_if_expired(int(secret[1]))
    #
    # response = SecretModelResponse()
    # return SecretModelResponse()
