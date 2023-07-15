from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from watchonceapi.dependencies.container import Container
from watchonceapi.routers.add_secret import add_secret_router
from watchonceapi.routers.get_secret import get_secret_router


def set_docs_schema(_app: FastAPI):
    openapi_schema = get_openapi(
        title="WatchONCE API", version="0.1.0", routes=_app.routes
    )

    _app.openapi_schema = openapi_schema
    return _app.openapi_schema


def create_app() -> FastAPI:
    container = Container()

    _app = FastAPI()
    _app.container = container

    _app.include_router(add_secret_router, prefix="/api")
    _app.include_router(get_secret_router, prefix="/api")
    set_docs_schema(_app)
    return _app


app = create_app()
