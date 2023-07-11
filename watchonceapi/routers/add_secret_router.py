from sqlite3 import Cursor
from typing import Annotated
import datetime

from fastapi import APIRouter, Depends
from pypika import Query

from watchonceapi.db_config import secrets_table
from watchonceapi.dependencies.db import get_db_cursor
from watchonceapi.models import SecretModel
from watchonceapi.services.add_secret_service import add_secret_to_db
from watchonceapi.utils.utils import get_expires_at, get_uuid

add_secret_router = APIRouter()


@add_secret_router.post("/add", response_model=SecretModel)
async def add_secret(
        secret: SecretModel,
        cursor: Annotated[Cursor, Depends(get_db_cursor)]
        ):

    add_secret_to_db(secret.text,
                     secret.expire_time,
                     cursor)
    return secret
