import datetime
import uuid


def get_expires_at(now_datetime, expire_value):
    if expire_value == 1:
        expires_at = now_datetime + datetime.timedelta(0, 0, 0, 0, 0, 1)
    elif expire_value == 2:
        expires_at = now_datetime + datetime.timedelta(1)
    else:
        expires_at = now_datetime + datetime.timedelta(0, 0, 0, 0, 10)

    return expires_at


def get_uuid():
    uuid_ = uuid.uuid4()
    return str(uuid_)
