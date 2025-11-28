from enum import Enum

class TaskType(Enum):
    PICKUP = "pickup"
    DELIVERY = "delivery"
    SCAN = "scan"
    WAIT = "wait"
