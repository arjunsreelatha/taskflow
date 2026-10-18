"""Domain exceptions for TaskFlow"""


class TaskFlowError(Exception):
    """Base class for all TaskFlow domain errors"""


class JobNotFound(TaskFlowError):
    pass


class InvalidTransition(TaskFlowError):
    """The requested state change is not allowed."""


class IdempotencyConflict(TaskFlowError):
    """an idempotency key was reused with a  different request body"""


class PermanentError(TaskFlowError):
    """An error indicating that the job has failed permanently and should not be retried."""
