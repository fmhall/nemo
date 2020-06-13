from collections import deque
from typing import Deque
from nemo.models import FullWork


class WorkQueue:
    work_deque: Deque[FullWork]

    def __init__(self):
        self.work_deque = deque()

    def add_work_item(self, item: FullWork):
        self.work_deque.append(item)

    def get_next_work_item(self) -> FullWork:
        return self.work_deque.pop()

    def __len__(self):
        return len(self.work_deque)


work_queue = WorkQueue()
