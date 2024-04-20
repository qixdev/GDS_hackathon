from datetime import datetime, UTC


def log(**kwargs):
    print(kwargs)
    ...


def log_time():
    return datetime.now(UTC)
