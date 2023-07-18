from minio import Minio
from pypika import Query

from watchonceapi.config import WATCHONCE_BUCKET_NAME
from watchonceapi.db_config import secrets_table, files_table
from watchonceapi.utils.connection_pool import ConnectionPool


async def remove_secret_from_db(uuid_: str, connection_pool: ConnectionPool):
    remove_secret_query = (
        Query.from_(secrets_table).delete().where(secrets_table.uuid == uuid_)
    )

    with connection_pool.connection() as connection:
        cursor = await connection.cursor()
        await cursor.execute(str(remove_secret_query))
        await cursor.close()
        await connection.commit()


async def remove_files_from_db(uuid_: str, connection_pool: ConnectionPool):
    remove_files_query = (
        Query.from_(files_table).delete().where(files_table.secret_id == uuid_)
    )

    with connection_pool.connection() as connection:
        cursor = await connection.cursor()
        await cursor.execute(str(remove_files_query))
        await cursor.close()
        await connection.commit()


def remove_files_from_minio(uuid_: str, client: Minio):
    client.remove_object(WATCHONCE_BUCKET_NAME, f"{uuid_}/")
