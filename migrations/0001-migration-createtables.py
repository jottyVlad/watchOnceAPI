from pypika import Query, Table, Column
from yoyo import step

secrets_table = Table("secrets")
files_table = Table("files")


CREATE_SECRETS_TABLE_IF_NOT_EXISTS = (
    Query.create_table(secrets_table)
    .columns(
        Column("uuid", "VARCHAR(36)", nullable=False),
        Column("text", "TEXT", nullable=True),
        Column("expires_at", "INTEGER", nullable=False),
    )
    .primary_key("uuid")
    .if_not_exists()
)

CREATE_FILES_TABLE_IF_NOT_EXISTS = (
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


DROP_SECRETS_TABLE = Query.drop_table(secrets_table)
DROP_FILES_TABLE = Query.drop_table(files_table)


steps = [
    step(
        str(CREATE_SECRETS_TABLE_IF_NOT_EXISTS),
        str(DROP_SECRETS_TABLE)
    ),
    step(
        str(CREATE_FILES_TABLE_IF_NOT_EXISTS),
        str(DROP_FILES_TABLE)
    )
]
