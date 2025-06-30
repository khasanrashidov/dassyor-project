from enum import Enum


class PhaseStatus(str, Enum):
    """Enum for phase status"""

    NOT_STARTED = "NotStarted"
    IN_PROGRESS = "InProgress"
    COMPLETED = "Completed"
