from datetime import datetime, timezone


def get_now_dt():
    return datetime.now(timezone.utc)