from pydantic import BaseModel, Field, field_validator

from taskflow.states import JobStatus


class Job(BaseModel):
    id: str = Field(min_length=1)
    task_name: str = Field(min_length=1)
    status: JobStatus = Field(default=JobStatus.PENDING)
    retries: int = Field(default=0, ge=0)

    @field_validator("task_name")
    @classmethod
    def validate_task_name(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("task_name cannot be empty or whitespace")
        return value


def create_job(job_id: str, task_name: str) -> Job:
    return Job(id=job_id, task_name=task_name)
