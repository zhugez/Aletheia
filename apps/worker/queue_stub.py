from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4


@dataclass
class IngestJob:
    job_id: str
    source_uri: str
    source_type: str
    status: str
    created_at: str


def create_ingest_job(source_uri: str, source_type: str = "book") -> IngestJob:
    # TODO: move to Redis queue producer
    return IngestJob(
        job_id=str(uuid4()),
        source_uri=source_uri,
        source_type=source_type,
        status="queued",
        created_at=datetime.utcnow().isoformat() + "Z",
    )
