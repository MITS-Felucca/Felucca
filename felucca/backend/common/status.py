from enum import Enum


class Status(Enum):
    Undefined = 0
    Pending = 1
    Running = 2
    Successful = 3
    Error = 4
    Failed = 5
    Killed = 6
    Finished = 7

    def __str__(self):
        return self.name
