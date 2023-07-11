import datetime
from sqlite3 import Cursor
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pypika import Query

from watchonceapi.db_config import secrets_table
from watchonceapi.dependencies.db import get_db_cursor

get_secret_router = APIRouter()


@get_secret_router.get("/get/{secret_id}")
async def get_secret(
        secret_id: str,
        cursor: Annotated[Cursor, Depends(get_db_cursor)]
):
    get_secret_query = Query. \
        from_(secrets_table). \
        select(secrets_table.secret, secrets_table.expires_at). \
        where(secrets_table.id == secret_id)

    result = cursor.execute(str(get_secret_query))
    secret = result.fetchone()

    # if secret is not exists
    if not secret:
        raise HTTPException(status_code=404, detail="Not found")

    remove_secret_query = Query. \
        from_(secrets_table). \
        delete(). \
        where(secrets_table.id == secret_id)

    cursor.execute(str(remove_secret_query))

    # if expired
    if int(secret[1]) <= datetime.datetime.now().timestamp():
        raise HTTPException(status_code=404, detail="Not found")

    # if not expired
    return {"secret": secret[0]}
