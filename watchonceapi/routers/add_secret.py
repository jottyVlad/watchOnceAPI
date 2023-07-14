from typing import List

from dependency_injector.wiring import inject
from fastapi import APIRouter, UploadFile, Request

from watchonceapi.services.add_secret import (
    add_secret_to_db,
    validated_secret_dto,
    add_files_to_db, add_files_to_minio, get_secret_url,
)

add_secret_router = APIRouter()


@add_secret_router.post("/add")
@inject
async def add_secret(
        request: Request,
        secret="{}",
        files: List[UploadFile] = (),
):
    secret_dto = validated_secret_dto(secret, files)
    await add_secret_to_db(secret_dto)
    await add_files_to_db(secret_dto)
    add_files_to_minio(secret_dto)

    return get_secret_url(secret_dto,
                          request.base_url.hostname,
                          request.base_url.port)
