from fastapi import APIRouter, Request

from watchonceapi.schema import ResponseSecretSchema
from watchonceapi.services.get_secret import get_secret_or_404, exception404_if_expired
from watchonceapi.services.remove_secret import remove_secret_from_db, remove_files_from_db

get_secret_router = APIRouter()


@get_secret_router.get("/get/{secret_id}", response_model=ResponseSecretSchema)
async def get_secret(request: Request,
                     secret_id: str):
    secret = get_secret_or_404(secret_id,
                               request.base_url.hostname,
                               request.base_url.port)
    remove_files_from_db(secret_id)
    remove_secret_from_db(secret_id)
    exception404_if_expired(secret.expires_at)

    return secret
