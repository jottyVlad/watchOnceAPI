import datetime
from typing import List, Optional

from dependency_injector.wiring import inject, Provide
from fastapi import UploadFile, HTTPException
from minio import Minio
from pydantic import ValidationError
from pypika import Query

from watchonceapi.config import WATCHONCE_BUCKET_NAME
from watchonceapi.db_config import secrets_table, files_table
from watchonceapi.dependencies.container import Container
from watchonceapi.schema import SecretDTO, SecretSchema
from watchonceapi.utils.connection_pool import ConnectionPool
from watchonceapi.utils.utils import get_uuid, get_expires_at


def validated_secret_dto(secret: str, files: List[UploadFile]) -> SecretDTO:
    try:
        validated_model = SecretSchema.model_validate_json(secret)
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


@inject
def add_secret_to_db(
        secret_dto: SecretDTO,
        connection_pool: ConnectionPool = Provide[Container.db_connection_pool]
):
    with connection_pool.connection() as connection:
        cursor = connection.cursor()
        add_query = Query.into(secrets_table).insert(
            secret_dto.uuid_,
            secret_dto.text,
            get_expires_at(datetime.datetime.now(), secret_dto.expire_time)
        )
        cursor.execute(str(add_query))
        cursor.close()


@inject
def add_files_to_minio(secret_dto,
                       client: Minio = Provide[Container.minio_client]):
    for file in secret_dto.files:
        filename = f'{secret_dto.uuid_}/{file.filename}'
        client.put_object(
            bucket_name=WATCHONCE_BUCKET_NAME,
            object_name=filename,
            data=file.file,
            length=-1,
            part_size=41943040,
        )


@inject
def add_files_to_db(secret_dto: SecretDTO,
                    connection_pool: ConnectionPool = Provide[Container.db_connection_pool]):
    add_file_to_db_query = Query.into(files_table)
    for file in secret_dto.files:
        filename = f'{secret_dto.uuid_}/{file.filename}'
        add_file_to_db_query.insert(filename, secret_dto.uuid_)

    with connection_pool.connection() as connection:
        cursor = connection.cursor()
        cursor.execute(str(add_file_to_db_query))
        cursor.close()


def get_secret_url(secret_dto: SecretDTO, base_url: str, port: Optional[int]):
    if port:
        return f'{base_url}:{port}/get/{secret_dto.uuid_}'
    else:
        return f'{base_url}/get/{secret_dto.uuid_}'
