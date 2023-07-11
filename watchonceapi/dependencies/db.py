from watchonceapi.db_config import con


def get_db_cursor():
    cur = con.cursor()
    try:
        yield cur
    finally:
        con.commit()
        cur.close()
