from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional

class JobStatus(str, Enum):
    received = "received"
    syncing = "syncing"
    deploying = "deploying"
    done = "done"
    failed_syncing = "failed_syncing"
    failed_deploying = "failed_deploying"

class Job(BaseModel):
    uid: UUID = Field(default_factory=uuid4)
    deploy_name: str = ""
    status: JobStatus = JobStatus.received
