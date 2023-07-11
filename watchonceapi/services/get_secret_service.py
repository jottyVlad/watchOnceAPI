import datetime

from fastapi import HTTPException
from pypika import Query

from watchonceapi.db_config import secrets_table


def get_secret_or_404(uuid_, cursor):
    get_secret_query = Query. \
        from_(secrets_table). \
        select(secrets_table.secret, secrets_table.expires_at). \
        where(secrets_table.id == uuid_)

    result = cursor.execute(str(get_secret_query))
    secret = result.fetchone()

    # if secret is not exists
    if not secret:
        raise HTTPException(status_code=404, detail="Not found")

    return secret


def exception404_if_expired(expires_at):
    if int(expires_at) <= datetime.datetime.now().timestamp():
        raise HTTPException(status_code=404, detail="Not found")
