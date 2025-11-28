from .TaskStatus import TaskStatus
import time

class Task:
    def __init__(self, ID, priority, task_type, target_pos, max_time):
        self.ID = ID
        self.priority = priority
        self.taskType = task_type
        self.aim_coordinants = target_pos
        self.max_time = max_time
        self.task_status = TaskStatus.PENDING
        self.start_time = None

    def __lt__(self, other_task):
        return self.priority < other_task.priority

    def start_task(self):
        self.task_status = TaskStatus.IN_PROGRESS
        self.start_time = time.time()

    def compelete_task(self):
        self.task_status = TaskStatus.COMPLETED

    def fail_task(self):
        self.task_status = TaskStatus.FAILED

    def timeout_task(self):
        self.task_status = TaskStatus.TIMEOUT

    def is_timed_out(self):
        if self.start_time is None:
            return False
        elapsed = time.time() - self.start_time
        return elapsed > self.max_time
