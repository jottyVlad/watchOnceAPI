import os

from minio import Minio


MINIO_ACCESS_KEY = os.getenv("MINIO_SERVER_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SERVER_SECRET_KEY")
WATCHONCE_BUCKET_NAME = "watchonce"
MINIO_URL = "172.20.0.2:9000"


def create_minio_client():
    client = Minio(
        MINIO_URL,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False
    )

    found = client.bucket_exists(WATCHONCE_BUCKET_NAME)
    if not found:
        client.make_bucket(WATCHONCE_BUCKET_NAME)

    return client
