from watchonceapi.storage_config import create_minio_client

client = create_minio_client()


def get_minio_client():
    return client
