from dependency_injector.wiring import inject, Provide
from minio import Minio
from pypika import Query

from watchonceapi.config import WATCHONCE_BUCKET_NAME
from watchonceapi.db_config import secrets_table, files_table
from watchonceapi.dependencies.container import Container
from watchonceapi.utils.connection_pool import ConnectionPool


@inject
def remove_secret_from_db(uuid_: str,
                          connection_pool: ConnectionPool = Provide[Container.db_connection_pool]):
    remove_secret_query = Query. \
        from_(secrets_table). \
        delete(). \
        where(secrets_table.uuid == uuid_)

    with connection_pool.connection() as connection:
        cursor = connection.cursor()
        cursor.execute(str(remove_secret_query))
        cursor.close()
        connection.commit()


@inject
def remove_files_from_db(uuid_: str,
                         connection_pool: ConnectionPool = Provide[Container.db_connection_pool]):
    remove_files_query = Query. \
        from_(files_table). \
        delete(). \
        where(files_table.secret_id == uuid_)

    with connection_pool.connection() as connection:
        cursor = connection.cursor()
        cursor.execute(str(remove_files_query))
        cursor.close()
        connection.commit()


@inject
def remove_files_from_minio(uuid_: str,
                            client: Minio = Provide[Container.minio_client]):
    client.remove_object(WATCHONCE_BUCKET_NAME,
                         f'{uuid_}/')
