import datetime
from typing import List, Optional, Tuple

from dependency_injector.wiring import inject, Provide
from fastapi import HTTPException
from minio import Minio
from pypika import Query

from watchonceapi.config import WATCHONCE_BUCKET_NAME
from watchonceapi.db_config import secrets_table, files_table
from watchonceapi.dependencies.container import Container
from watchonceapi.schema import ResponseSecretSchema, DBGetSecretTuple
from watchonceapi.services.remove_secret import (
    remove_files_from_db,
    remove_secret_from_db,
)
from watchonceapi.utils.connection_pool import ConnectionPool


def get_file_download_url(base_url: str, port: Optional[int], filepath: str):
    if port:
        return f"{base_url}:{port}/api/dfile/{filepath}"
    else:
        return f"{base_url}/api/dfile/{filepath}"


@inject
def get_files_links(
    filepaths: List[str], client: Minio = Provide[Container.minio_client]
) -> List[str]:
    files = []
    for filepath in filepaths:
        url: str = client.get_presigned_url(
            "GET",
            WATCHONCE_BUCKET_NAME,
            filepath,
            expires=datetime.timedelta(minutes=10),
        )
        files.append(url)
    return files


async def get_secret_or_404(
    uuid_: str, connection_pool: ConnectionPool
) -> ResponseSecretSchema:
    get_secret_query = (
        Query.from_(secrets_table)
        .select(secrets_table.text, secrets_table.expires_at)
        .where(secrets_table.uuid == uuid_)
    )

    get_files_query = (
        Query.from_(files_table)
        .select(files_table.filepath)
        .where(files_table.secret_id == uuid_)
    )

    with connection_pool.connection() as connection:
        cursor = await connection.cursor()
        result = await cursor.execute(str(get_secret_query))
        secret = await result.fetchone()
        await cursor.close()

    if not secret:
        raise HTTPException(status_code=404, detail="Secret not found")
    else:
        secret = DBGetSecretTuple._make(secret)

    with connection_pool.connection() as connection:
        cursor = await connection.cursor()
        result = await cursor.execute(str(get_files_query))
        filepaths = await result.fetchall()
        filepaths = [filepath[0] for filepath in filepaths]
        await cursor.close()

    files = get_files_links(filepaths)

    expires_at = datetime.datetime.strptime(secret.expires_at, "%Y-%m-%dT%H:%M:%S.%f")
    return ResponseSecretSchema(text=secret.text, files=files, expires_at=expires_at)


def check_expired(expires_at: datetime.datetime):
    if expires_at.timestamp() <= datetime.datetime.now().timestamp():
        raise HTTPException(status_code=404, detail="Not found")


async def process_get_secret_request(
    secret_id: str, connection_pool: ConnectionPool
) -> ResponseSecretSchema:
    secret = await get_secret_or_404(secret_id, connection_pool)
    await remove_files_from_db(secret_id, connection_pool)
    await remove_secret_from_db(secret_id, connection_pool)
    check_expired(secret.expires_at)

    return secret
