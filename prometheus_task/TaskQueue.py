from typing import List, Optional
from .Task import Task

class TaskQueue:
    def __init__(self):
        self.task_queue : List[Task] = []
        self.current : Optional[Task] = None

    def enqueue(self, task : Task):
        self.task_queue.append(task)
        self.task_queue.sort()

    def pop(self):
        if len(self.task_queue) == 0:
            print("There is no next task")
            return None

        return self.task_queue.pop(0)

    def get_next_task(self):
        if self.current is not None:
            print(f"Busy! Task {self.current.ID} is still running.")
            return None

        next_task = self.pop()

        if next_task == None:
            print("Queue is empty")
            return None

        self.current = next_task
        self.current.start_task()
        return self.current

    def complete_current_task(self):
        if self.current == None:
            print("There is no current task")
            return None

        print(f"Task {self.current.ID} finished.")
        self.current.compelete_task()
        self.current = None

    def fail_current_task(self):
        if self.current == None:
            print("There is no current task")
            return None

        print(f"Task {self.current.ID} failed.")
        self.current.fail_task()
        self.current = None

    def timeout_current_task(self):
        if self.current == None:
            print("There is no current task")
            return None

        print(f"Task {self.current.ID} timed out.")
        self.current.timeout_task()
        self.current = None
