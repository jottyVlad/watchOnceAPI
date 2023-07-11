import sqlite3

from pypika import Table

from watchonceapi.config import DATABASE_DIRECTORY

con = sqlite3.connect(DATABASE_DIRECTORY,
                      check_same_thread=False)

secrets_table = Table("secrets")
