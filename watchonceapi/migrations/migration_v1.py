import sqlite3

from pypika import Query, Column

from watchonceapi.config import DATABASE_DIRECTORY
from watchonceapi.db_config import secrets_table, files_table


def migration_v1():
    connection = sqlite3.connect(DATABASE_DIRECTORY, check_same_thread=False)
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
            Column("filepath", "VARCHAR(1000)", nullable=False),
            Column("secret_id", "VARCHAR(36)", nullable=False),
        )
        .foreign_key(
            columns=["secret_id"],
            reference_table=secrets_table,
            reference_columns=["id"],
        )
        .if_not_exists()
    )

    transaction = (
        f"{create_secrets_table_if_not_exist_query};"
        f"{create_files_table_if_not_exist_query}"
    )

    cur.executescript(transaction)
    cur.close()
    connection.commit()
    connection.close()
