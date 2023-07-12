from pypika import Query

from watchonceapi.db_config import secrets_table


def remove_secret_from_db(uuid_, cursor):
    remove_secret_query = Query. \
        from_(secrets_table). \
        delete(). \
        where(secrets_table.id == uuid_)

    cursor.execute(str(remove_secret_query))
