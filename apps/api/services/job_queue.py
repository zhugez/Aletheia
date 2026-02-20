from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

try:
    from redis import Redis
    from rq import Queue
    from rq.job import Job
except Exception:  # pragma: no cover
    Redis = None
    Queue = None
    Job = None


@dataclass
class QueueConfig:
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    queue_name: str = os.getenv("ALETHEIA_QUEUE", "aletheia_ingest")


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_queue() -> Queue | None:
    if Redis is None or Queue is None:
        return None
    try:
        conn = Redis.from_url(QueueConfig().redis_url)
        conn.ping()
        return Queue(QueueConfig().queue_name, connection=conn)
    except Exception:
        return None


def enqueue_ingest(source_uri: str, source_type: str = "book", metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    queue = get_queue()
    if queue is None:
        return {
            "job_id": None,
            "status": "queue_unavailable",
            "source_uri": source_uri,
            "source_type": source_type,
            "created_at": _utcnow(),
        }

    payload = {"source_uri": source_uri, "source_type": source_type, "metadata": metadata or {}}
    job = queue.enqueue("worker.runner.process_ingest_job", payload, retry=3, job_timeout=1200)
    return {
        "job_id": job.id,
        "status": "queued",
        "source_uri": source_uri,
        "source_type": source_type,
        "created_at": _utcnow(),
    }


def get_job_status(job_id: str) -> dict[str, Any]:
    queue = get_queue()
    if queue is None or Job is None:
        return {"job_id": job_id, "status": "queue_unavailable"}

    try:
        job = Job.fetch(job_id, connection=queue.connection)
    except Exception:
        return {"job_id": job_id, "status": "not_found"}

    result: dict[str, Any] = {
        "job_id": job.id,
        "status": job.get_status(refresh=True),
        "enqueued_at": job.enqueued_at.isoformat() if job.enqueued_at else None,
        "started_at": job.started_at.isoformat() if job.started_at else None,
        "ended_at": job.ended_at.isoformat() if job.ended_at else None,
    }
    if job.is_finished:
        result["result"] = job.result
    if job.is_failed:
        result["error"] = job.exc_info
    return result
