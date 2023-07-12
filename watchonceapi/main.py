import sqlite3

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from watchonceapi.config import DATABASE_DIRECTORY
from watchonceapi.db_config import init_db_tables
from watchonceapi.dependencies.container import Container
from watchonceapi.routers.add_secret import add_secret_router
# from watchonceapi.routers.get_secret import get_secret_router


def set_docs_schema(_app: FastAPI):
    openapi_schema = get_openapi(
        title="WatchONCE API",
        version="0.1.0",
        routes=_app.routes
    )

    _app.openapi_schema = openapi_schema
    return _app.openapi_schema


def create_app() -> FastAPI:
    container = Container()

    app = FastAPI()
    app.container = container

    # TODO: delete initializing tables on server start
    connection = sqlite3.connect(DATABASE_DIRECTORY, check_same_thread=False)
    init_db_tables(connection)
    connection.close()
    # END TODO

    app.include_router(add_secret_router, prefix="/api")
    # app.include_router(get_secret_router, prefix="/api")
    set_docs_schema(app)
    return app


app = create_app()
