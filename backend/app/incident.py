from pydantic import BaseModel, ConfigDict, field_validator, Field
from datetime import datetime
from uuid import UUID

MAX_JOB_NAME_LENGTH = 200
MAX_LOG_BYTES = 64 * 1024  # 64 KiB

class IncidentCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    job_name: str
    log: str
    exit_code: int | None = Field(default=None, ge=-(2**31), le=2**31 - 1)

    @field_validator("job_name")
    @classmethod
    def validate_job_name(cls, value: str) -> str:
        name = value.strip()

        if not name:
            raise ValueError("Job name cannot be empty")

        if len(name) > MAX_JOB_NAME_LENGTH:
            raise ValueError(f"Job name cannot exceed {MAX_JOB_NAME_LENGTH} characters")

        return name

    @field_validator("log")
    @classmethod
    def validate_log(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Log cannot be empty")

        if len(value.encode("utf-8")) > MAX_LOG_BYTES:
            raise ValueError(f"Log cannot exceed {MAX_LOG_BYTES} bytes")

        return value

class IncidentResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    job_name: str
    log: str
    exit_code: int | None
    created_at: datetime

class IncidentListResponse(BaseModel):
    items: list[IncidentResponse]
    limit: int
    offset: int
