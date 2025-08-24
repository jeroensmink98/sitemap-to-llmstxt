from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from enum import Enum

class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class JobRequest(BaseModel):
    domain: str
    output: Optional[str] = None  # Changed from output_filename to match CLI
    batch_size: int = 10
    batch_delay: int = 1000
    include_metadata: bool = False

class JobResponse(BaseModel):
    job_id: str
    status: JobStatus
    message: str
    output: Optional[str] = None  # The filename that will be generated

class JobStatusResponse(BaseModel):
    job_id: str
    status: JobStatus
    progress: Optional[float] = None
    message: Optional[str] = None
    created_at: str
    updated_at: str

class JobResultResponse(BaseModel):
    job_id: str
    status: JobStatus
    output_file: str
    url_count: int
    download_url: str