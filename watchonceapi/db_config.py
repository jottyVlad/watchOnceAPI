import sqlite3
from sqlite3 import Connection

from pypika import Table, Query, Column

from watchonceapi.config import DATABASE_DIRECTORY

con = sqlite3.connect(DATABASE_DIRECTORY,
                      check_same_thread=False)

secrets_table = Table("secrets")
files_table = Table("files")


def init_db_tables(connection: Connection):
    cur = connection.cursor()
    create_secrets_table_if_not_exist_query = Query. \
        create_table(secrets_table). \
        columns(
        Column("id", "VARCHAR(32)", nullable=False),
        Column("secret", "VARCHAR(1000)", nullable=True),
        Column("expires_at", "INTEGER", nullable=False)
    ). \
        primary_key("id"). \
        if_not_exists()

    create_files_table_if_not_exist_query = Query. \
        create_table(files_table). \
        columns(
        Column("id", "INTEGER", nullable=False),
        Column("filename", "VARCHAR(1000)", nullable=False),
        Column("secret_id", "VARCHAR(32)", nullable=False)
    ). \
        foreign_key(
        columns=["secret_id"],
        reference_table=secrets_table,
        reference_columns=["id"]
    ). \
        primary_key("id"). \
        if_not_exists()

    cur.execute(str(create_secrets_table_if_not_exist_query))
    cur.execute(str(create_files_table_if_not_exist_query))
    cur.close()


def close_db_connection(connection: Connection):
    connection.close()
