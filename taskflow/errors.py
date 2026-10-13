'''Domain exceptions for TaskFlow'''


class TaskFlowError(Exception):
 """Base class for all TaskFlow domain errors"""
class JobNotFound(TaskFlowError):
    pass

class InvalidTransaction(TaskFlowError):
  """The requested state change is not allowed."""

class IdempotencyConflict(TaskFlowError):

 """an idempotency key was reused with a  differnt request body"""