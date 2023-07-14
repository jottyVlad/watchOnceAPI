from dependency_injector import containers, providers

from watchonceapi.storage_config import create_minio_client
from watchonceapi.utils.connection_pool import ConnectionPool
from watchonceapi.config import (
    MINIO_SECRET_KEY,
    MINIO_ACCESS_KEY,
    MINIO_URL,
    WATCHONCE_BUCKET_NAME,
    DATABASE_DIRECTORY,
)


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        packages=["watchonceapi.routers", "watchonceapi.services"]
    )

    db_connection_pool = providers.Factory(
        ConnectionPool.create, max_connections=10, database=DATABASE_DIRECTORY
    )
    minio_client = providers.Factory(
        create_minio_client,
        minio_url=MINIO_URL,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        bucket_name=WATCHONCE_BUCKET_NAME,
    )
