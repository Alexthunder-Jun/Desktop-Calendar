from enum import Enum


class AlarmMode(str, Enum):
    COUNTDOWN = "countdown"
    SCHEDULED = "scheduled"


class AlarmStatus(str, Enum):
    PENDING = "pending"
    FIRED = "fired"
    CANCELLED = "cancelled"
