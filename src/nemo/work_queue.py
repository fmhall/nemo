from collections import deque
from typing import Deque, Dict, Optional
from nemo.models import FullWork, Work
import uuid


class WorkQueue:

    work_deque: Deque[FullWork]
    assigned_work: Dict[str, FullWork]

    def __init__(self):
        self.work_deque = deque()
        self.assigned_work = dict()

    def add_work_item(self, item: FullWork):
        self.work_deque.append(item)
        self.assign_work_item(item)

    def get_next_work_item(self) -> Optional[FullWork]:
        if self.work_deque:
            return self.work_deque.pop()

    def assign_work_item(self, item: FullWork):
        if item.work.type in self.assigned_work:
            print("Item is already assigned")
        else:
            self.assigned_work[item.work.type] = item

    def __len__(self):
        return len(self.work_deque)


work_queue = WorkQueue()

work = Work(type="analysis", id=uuid.uuid4())
print(work)
response = FullWork(
    work=work,
    game_id="abcdefgh",
    position="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
    moves="e2e4 c7c5 c2c4 b8c6 g1e2 g8f6 b1c3 c6b4 g2g3 b4d3",
    nodes=3500000,
    skipPositions=[1, 4, 5],
)
work_queue.add_work_item(response)