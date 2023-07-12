from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from watchonceapi.db_config import con, init_db_tables, close_db_connection
from watchonceapi.dependencies.minio import get_minio_client
from watchonceapi.routers.add_secret_router import add_secret_router
from watchonceapi.routers.get_secret_router import get_secret_router

app = FastAPI()


@app.on_event("startup")
def on_startup():
    init_db_tables(con)
    get_minio_client()


@app.on_event("shutdown")
def on_shutdown():
    close_db_connection(con)


def set_docs_schema(_app: FastAPI):
    openapi_schema = get_openapi(
        title="WatchONCE API",
        version="0.1.0",
        routes=_app.routes
    )

    _app.openapi_schema = openapi_schema
    return _app.openapi_schema


app.include_router(add_secret_router, prefix="/api")
app.include_router(get_secret_router, prefix="/api")
set_docs_schema(app)
