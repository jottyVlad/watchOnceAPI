import datetime
from sqlite3 import Cursor
from typing import IO

from fastapi import HTTPException, File
from minio import Minio
from pypika import Query

from watchonceapi.db_config import secrets_table, files_table
from watchonceapi.models import GetSecretModel
from watchonceapi.storage_config import WATCHONCE_BUCKET_NAME


def get_secret_or_404(uuid_: str, cursor: Cursor, minio: Minio) -> GetSecretModel:
    get_secret_query = Query. \
        from_(secrets_table). \
        select(secrets_table.secret, secrets_table.expires_at). \
        where(secrets_table.id == uuid_)

    get_files_query = Query .\
        from_(files_table). \
        select(files_table.filename). \
        where(files_table.secret_id == uuid_)

    result = cursor.execute(str(get_secret_query))
    secret = result.fetchone()

    # if secret is not exists
    if not secret:
        raise HTTPException(status_code=404, detail="Not found")

    result = cursor.execute(str(get_files_query))
    filenames = result.fetchall()

    files = []
    if filenames:
        for filename in filenames:
            file = minio.get_object(
                WATCHONCE_BUCKET_NAME,
                filename
            )
            with open(f'/files/{filename}', 'wb') as data_file:
                for d in file.stream(32*1024):
                    data_file.write(d)
            files.append(f'/files/{filename}')

    return GetSecretModel(text=secret[0], files=files)


def exception404_if_expired(expires_at):
    if int(expires_at) <= datetime.datetime.now().timestamp():
        raise HTTPException(status_code=404, detail="Not found")
