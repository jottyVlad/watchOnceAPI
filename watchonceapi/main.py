from sqlite3 import Connection

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from pypika import Query, Column

from watchonceapi.db_config import con, secrets_table
from watchonceapi.routers.add_secret_router import add_secret_router
from watchonceapi.routers.get_secret_router import get_secret_router

app = FastAPI()


def init_db_tables(connection: Connection):
    cur = connection.cursor()
    create_table_if_not_exist_query = Query. \
        create_table(secrets_table). \
        columns(
            Column("id", "VARCHAR(32)", nullable=False),
            Column("secret", "VARCHAR(1000)", nullable=False),
            Column("expires_at", "INTEGER", nullable=False)
        ). \
        primary_key("id"). \
        if_not_exists()

    cur.execute(str(create_table_if_not_exist_query))
    cur.close()


def close_db_connection(connection: Connection):
    connection.close()


@app.on_event("startup")
def on_startup():
    init_db_tables(con)


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
