from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

try:
    from redis import Redis
    from rq import Queue, Retry
    from rq.job import Job
except Exception:  # pragma: no cover
    Redis = None
    Queue = None
    Retry = None
    Job = None

_REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
_QUEUE_NAME = os.getenv("ALETHEIA_QUEUE", "aletheia_ingest")
_queue: Queue | None = None


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_queue() -> Queue | None:
    global _queue
    if Redis is None or Queue is None:
        return None
    if _queue is not None:
        try:
            _queue.connection.ping()
            return _queue
        except Exception:
            _queue = None
    try:
        conn = Redis.from_url(_REDIS_URL)
        conn.ping()
        _queue = Queue(_QUEUE_NAME, connection=conn)
        return _queue
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
    retry_policy = Retry(max=3) if Retry is not None else None
    job = queue.enqueue("runner.process_ingest_job", payload, retry=retry_policy, job_timeout=1200)
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


def cancel_job(job_id: str) -> dict[str, Any]:
    queue = get_queue()
    if queue is None or Job is None:
        return {"job_id": job_id, "status": "queue_unavailable"}

    try:
        job = Job.fetch(job_id, connection=queue.connection)
        job.cancel()
        return {"job_id": job_id, "status": "canceled"}
    except Exception:
        return {"job_id": job_id, "status": "not_found"}


def retry_job(job_id: str) -> dict[str, Any]:
    queue = get_queue()
    if queue is None or Job is None:
        return {"job_id": job_id, "status": "queue_unavailable"}

    try:
        from rq.registry import FailedJobRegistry
        registry = FailedJobRegistry(queue=queue)
        registry.requeue(job_id)
        return {"job_id": job_id, "status": "queued"}
    except Exception:
        return {"job_id": job_id, "status": "not_found_in_failed_registry"}
