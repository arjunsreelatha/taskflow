
from pydantic import BaseModel, ConfigDict, Field, field_validator

from taskflow.states import JobStatus, assert_transition


class Job(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    id: str = Field(min_length=1)
    task_name: str = Field(min_length=1)
    status: JobStatus = Field(default=JobStatus.PENDING)
    retries: int = Field(default=0, ge=0)

    @field_validator("task_name")
    @classmethod
    def validate_task_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("task_name cannot be empty or whitespace")
        return value

    def __setattr__(self, name: str, value) -> None:
        if name == "status" and "status" in self.__dict__:
            new_status = (
                value if isinstance(value, JobStatus) else JobStatus(value)
            )
            assert_transition(self.status, new_status)
            value = new_status

        super().__setattr__(name, value)

    def transition_to(self, new_status: JobStatus) -> None:
        assert_transition(self.status, new_status)
        self.status = new_status


def create_job(job_id: str, task_name: str) -> Job:
    return Job(id=job_id, task_name=task_name)
