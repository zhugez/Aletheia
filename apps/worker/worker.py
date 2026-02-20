from __future__ import annotations

import os

from redis import Redis
from rq import Connection, Worker


def main() -> None:
    redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
    queue_name = os.getenv("ALETHEIA_QUEUE", "aletheia_ingest")
    conn = Redis.from_url(redis_url)

    with Connection(conn):
        worker = Worker([queue_name])
        worker.work(with_scheduler=False)


if __name__ == "__main__":
    main()
