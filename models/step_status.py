from enum import Enum


class StepStatus(Enum):
    DONE = "Done"
    PENDING = "Pending"
    BLOCKED = "Blocked"
    NOT_RELEVANT = "Not Relevant"
    UNDECIDED = "Undecided"
