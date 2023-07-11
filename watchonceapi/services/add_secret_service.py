import datetime

from pypika import Query

from watchonceapi.db_config import secrets_table
from watchonceapi.utils.utils import get_uuid, get_expires_at


def add_secret_to_db(text, expire_time, cursor):
    add_query = Query. \
        into(secrets_table). \
        insert(get_uuid(),
               text,
               get_expires_at(
                   datetime.datetime.now(),
                   expire_time)
               )
    cursor.execute(str(add_query))