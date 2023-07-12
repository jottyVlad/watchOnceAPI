import datetime
from sqlite3 import Cursor
from typing import Optional, List

from fastapi import UploadFile, HTTPException
from minio import Minio
from pypika import Query

from watchonceapi.db_config import secrets_table, files_table
from watchonceapi.models import SecretModel
from watchonceapi.storage_config import WATCHONCE_BUCKET_NAME
from watchonceapi.utils.utils import get_uuid, get_expires_at


def check_files_and_text_status_or_404(secret: SecretModel,
                                       files: Optional[List[UploadFile]]) -> int:
    if files:
        return 2
    elif secret.text and not files:
        return 1
    else:
        raise HTTPException(status_code=400)


def handle_status(status: int,
                  secret: SecretModel,
                  files: Optional[List[UploadFile]],
                  cursor: Cursor,
                  client: Minio):
    uuid = get_uuid()
    if status == 1:
        add_secret_to_db(secret.text,
                         secret.expire_time,
                         uuid,
                         cursor)
    elif status == 2:
        add_secret_to_db(secret.text,
                         secret.expire_time,
                         uuid,
                         cursor)
        add_files_to_minio(files, client)
        add_files_to_db(files, uuid, cursor)


def add_files_to_minio(files: List[UploadFile],
                       client: Minio):
    for file in files:
        client.put_object(
            bucket_name=WATCHONCE_BUCKET_NAME,
            object_name=file.filename,
            data=file.file,
            length=-1,
            part_size=41943040
        )


def add_files_to_db(files: List[UploadFile],
                    uuid: str,
                    cursor: Cursor):
    for file in files:
        add_file_to_db_query = Query. \
            into(files_table). \
            insert(file.filename,
                   uuid)
        cursor.execute(str(add_file_to_db_query))


def add_secret_to_db(text,
                     expire_time,
                     uuid,
                     cursor):
    add_query = Query. \
        into(secrets_table). \
        insert(uuid,
               text,
               get_expires_at(
                   datetime.datetime.now(),
                   expire_time)
               )
    cursor.execute(str(add_query))
