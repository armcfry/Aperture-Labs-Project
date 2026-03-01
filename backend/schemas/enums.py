from enum import Enum


class ProjectRole(str, Enum):
    owner = "owner"
    editor = "editor"
    viewer = "viewer"


class SubmissionStatus(str, Enum):
    queued = "queued"
    running = "running"
    complete = "complete"
    complete_with_errors = "complete_with_errors"
    failed = "failed"


class SubmissionPassFail(str, Enum):
    pass_ = "pass"
    fail = "fail"
    unknown = "unknown"

    @property
    def db_value(self) -> str:
        return "pass" if self is SubmissionPassFail.pass_ else self.value


class AnomalySeverity(str, Enum):
    low = "low"
    med = "med"
    high = "high"