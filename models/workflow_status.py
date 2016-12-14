from enum import Enum


class WorkflowStatus(Enum):
    IN_PROGRESS = "In Progress"
    ABANDONED = "Abandoned"
    PAUSED = "Paused"
    FINISHED = "Finished"
