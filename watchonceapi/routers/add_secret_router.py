from sqlite3 import Cursor
from typing import Annotated
import hashlib
import datetime

from fastapi import APIRouter, Request, HTTPException, Depends
from pypika import Query

from watchonceapi.db_config import secrets_table
from watchonceapi.dependencies.db import get_db_cursor
from watchonceapi.models import SecretModel

add_secret_router = APIRouter()


@add_secret_router.post("/add", response_model=SecretModel)
async def add_secret(
        secret: SecretModel,
        cursor: Annotated[Cursor, Depends(get_db_cursor)]
        ):

    now_datetime = datetime.datetime.now()
    hashing_string = secret.text + str(now_datetime)
    hashed = hashlib.md5(hashing_string.encode()).hexdigest()
    if secret.expire_time == 1:
        expires_at = now_datetime + datetime.timedelta(0, 0, 0, 0, 0, 1)
    elif secret.expire_time == 2:
        expires_at = now_datetime + datetime.timedelta(1)
    else:
        expires_at = now_datetime + datetime.timedelta(0, 0, 0, 0, 10)
        secret.expire_time = 0

    expires_at = int(expires_at.timestamp())
    add_query = Query.into(secrets_table).insert(hashed, secret.text, expires_at)
    cursor.execute(str(add_query))
    return secret
