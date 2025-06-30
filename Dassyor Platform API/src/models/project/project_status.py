from enum import Enum


class ProjectStatus(str, Enum):
    """Enum for project status"""

    IN_PROGRESS = "InProgress"
    COMPLETED = "Completed"
