import datetime
from typing import List, Optional, Union

from fastapi import UploadFile, HTTPException, Request
from minio import Minio
from pydantic import ValidationError
from pypika import Query

from watchonceapi.config import WATCHONCE_BUCKET_NAME
from watchonceapi.db_config import secrets_table
from watchonceapi.schema import SecretDTO, SecretSchema
from watchonceapi.utils.connection_pool import ConnectionPool
from watchonceapi.utils.utils import get_uuid, get_expires_at


def validate_secret(secret: str, files: List[UploadFile]) -> SecretDTO:
    try:
        validated_model = SecretSchema.model_validate_json(secret)
        if not validated_model.text and not files:
            raise ValidationError
    except ValidationError:
        raise HTTPException(
            status_code=400,
            detail='Object must contain only "text" (optional) and '
            '"expire_time" (optional)',
        )
    return SecretDTO(
        uuid_=get_uuid(),
        text=validated_model.text,
        expire_time=validated_model.expire_time,
        files=files,
    )


async def add_secret_to_db(
    secret_dto: SecretDTO,
    connection_pool: ConnectionPool,
):
    with connection_pool.connection() as connection:
        cursor = await connection.cursor()
        add_query = Query.into(secrets_table).insert(
            secret_dto.uuid_,
            secret_dto.text,
            get_expires_at(datetime.datetime.now(), secret_dto.expire_time),
        )
        await cursor.execute(str(add_query))
        await cursor.close()
        await connection.commit()


def add_files_to_minio(secret_dto, client: Minio):
    for file in secret_dto.files:
        filename = f"{secret_dto.uuid_}/{file.filename}"
        client.put_object(
            bucket_name=WATCHONCE_BUCKET_NAME,
            object_name=filename,
            data=file.file,
            length=-1,
            part_size=41943040,
        )


async def add_files_to_db(
    secret_dto: SecretDTO,
    connection_pool: ConnectionPool,
):
    add_file_to_db_query = "INSERT INTO `files` VALUES (?, ?)"

    data = [
        (f"{secret_dto.uuid_}/{file.filename}", secret_dto.uuid_)
        for file in secret_dto.files
    ]

    with connection_pool.connection() as connection:
        cursor = await connection.cursor()
        await cursor.executemany(add_file_to_db_query, data)
        await cursor.close()
        await connection.commit()


def get_secret_url(secret_dto: SecretDTO, base_url: str, port: Optional[int]):
    if port:
        return f"{base_url}:{port}/api/get/{secret_dto.uuid_}"
    else:
        return f"{base_url}/api/get/{secret_dto.uuid_}"


async def process_add_secret_request(
    request: Request,
    secret: str,
    files: Union[List[UploadFile], str],
    connection_pool: ConnectionPool,
    minio_client: Minio,
) -> str:

    if not files or not files[0].filename:
        files = []
    if secret == "":
        secret = "{}"
    secret_dto = validate_secret(secret, files)
    await add_secret_to_db(secret_dto, connection_pool)
    await add_files_to_db(secret_dto, connection_pool)
    add_files_to_minio(secret_dto, minio_client)
    return get_secret_url(secret_dto, request.base_url.hostname, request.base_url.port)
