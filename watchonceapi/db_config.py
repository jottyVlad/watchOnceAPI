import sqlite3
from sqlite3 import Connection

from pypika import Table, Query, Column


secrets_table = Table("secrets")
files_table = Table("files")


def init_db_tables(connection: Connection):
    cur = connection.cursor()
    create_secrets_table_if_not_exist_query = (
        Query.create_table(secrets_table)
        .columns(
            Column("uuid", "VARCHAR(36)", nullable=False),
            Column("text", "TEXT", nullable=True),
            Column("expires_at", "INTEGER", nullable=False),
        )
        .primary_key("uuid")
        .if_not_exists()
    )

    create_files_table_if_not_exist_query = (
        Query.create_table(files_table)
        .columns(
            Column("filename", "VARCHAR(1000)", nullable=False),
            Column("secret_id", "VARCHAR(36)", nullable=False),
        )
        .foreign_key(
            columns=["secret_id"],
            reference_table=secrets_table,
            reference_columns=["id"],
        )
        .if_not_exists()
    )

    transaction = f"{create_secrets_table_if_not_exist_query};" \
                  f"{create_files_table_if_not_exist_query}"

    cur.executescript(transaction)
    cur.close()


def close_db_connection(connection: Connection):
    connection.close()
