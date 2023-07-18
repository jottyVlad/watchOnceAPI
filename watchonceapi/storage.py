from minio import Minio


def create_minio_client(
    minio_url: str, access_key: str, secret_key: str, bucket_name: str
) -> Minio:
    client = Minio(
        minio_url, access_key=access_key, secret_key=secret_key, secure=False
    )

    found = client.bucket_exists(bucket_name)
    if not found:
        client.make_bucket(bucket_name)

    return client
