from typing import List, Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, UploadFile, Request, Form, Depends
from minio import Minio

from watchonceapi.dependencies.container import Container
from watchonceapi.schema import ResponseSecretSchema
from watchonceapi.services.add_secret import (
    process_add_secret_request,
)
from watchonceapi.services.get_secret import process_get_secret_request
from watchonceapi.utils.connection_pool import ConnectionPool

api_secret_router = APIRouter()


@api_secret_router.post("/add")
@inject
async def add_secret(
    request: Request,
    secret: Annotated[str, Form()] = "{}",
    files: List[UploadFile] = "",
    connection_pool: ConnectionPool = Depends(Provide[Container.db_connection_pool]),
    minio_client: Minio = Depends(Provide[Container.minio_client]),
):
    return await process_add_secret_request(
        request, secret, files, connection_pool, minio_client
    )


@api_secret_router.get("/get/{secret_id}", response_model=ResponseSecretSchema)
@inject
async def get_secret(
    secret_id: str,
    connection_pool: ConnectionPool = Depends(Provide[Container.db_connection_pool]),
):
    return await process_get_secret_request(secret_id, connection_pool)
