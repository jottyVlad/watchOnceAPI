import datetime
from sqlite3 import Cursor
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pypika import Query

from watchonceapi.db_config import secrets_table
from watchonceapi.dependencies.db import get_db_cursor
from watchonceapi.services.get_secret_service import get_secret_or_404, exception404_if_expired
from watchonceapi.services.remove_secret_service import remove_secret_from_db

get_secret_router = APIRouter()


@get_secret_router.get("/get/{secret_id}")
async def get_secret(
        secret_id: str,
        cursor: Annotated[Cursor, Depends(get_db_cursor)]
):
    secret = get_secret_or_404(secret_id, cursor)
    remove_secret_from_db(secret_id, cursor)
    exception404_if_expired(int(secret[1]))

    return {"secret": secret[0]}
