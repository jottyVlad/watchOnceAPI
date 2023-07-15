from typing import List, Annotated

from fastapi import APIRouter, UploadFile, Request, Form

from watchonceapi.services.add_secret import (
    add_secret_to_db,
    validated_secret_dto,
    add_files_to_db,
    add_files_to_minio,
    get_secret_url,
)

add_secret_router = APIRouter()


@add_secret_router.post("/add")
async def add_secret(
    request: Request,
    secret: Annotated[str, Form()] = "{}",
    files: List[UploadFile] = "",
):
    if not files or not files[0].filename:
        files = []
    if secret == "":
        secret = "{}"
    secret_dto = validated_secret_dto(secret, files)
    await add_secret_to_db(secret_dto)
    await add_files_to_db(secret_dto)
    add_files_to_minio(secret_dto)

    return get_secret_url(secret_dto, request.base_url.hostname, request.base_url.port)
