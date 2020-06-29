from collections import deque
from typing import Deque, Dict, Optional, Set, List
from nemo.models import FullWork, Work, Analysis
import uuid
import logging

logger = logging.getLogger(__name__)


class WorkQueue:
    """
    Work Queue for engine analysis work
    Also stores game analysis information
    TODO: Split into multiple data structures, switch to async, redis(?)
    """

    work_deque: Deque[FullWork]
    assigned_work: Dict[str, FullWork]
    assigned_analysis: Dict[uuid.UUID, List[Optional[Analysis]]]
    retired_work: Set[uuid.UUID]
    game_url_to_uuid: Dict[str, uuid.UUID]

    def __init__(self):
        self.work_deque = deque()
        self.assigned_work: Dict[uuid.UUID, FullWork] = dict()
        self.assigned_analysis: Dict[uuid.UUID, List[Optional[Analysis]]] = dict()
        self.retired_work: Set[uuid.UUID] = set()
        self.game_url_to_uuid: Dict[str, uuid.UUID] = dict()

    def add_work_item(self, item: FullWork):
        self.work_deque.append(item)
        self.assign_work_item(item)
        self.game_url_to_uuid[item.game_id] = item.work.id

    def get_next_work_item(self) -> Optional[FullWork]:
        if self.work_deque:
            return self.work_deque.pop()

    def assign_work_item(self, item: FullWork):
        if item.work.id in self.assigned_work:
            logger.debug("Item is already assigned")
        else:
            self.assigned_work[item.work.id] = item
            logger.debug(f"Assigned {item.work.id} to {item}")
            logger.debug(self.assigned_work)

    def retire_work_item(self, work_id: uuid.UUID) -> None:
        if work_id in self.assigned_work:
            logger.debug(f"Removing {work_id} from assigned work")
            del self.assigned_work[work_id]
            self.retired_work.add(work_id)
        elif work_id in self.retired_work:
            logger.warning(
                f"Tried to retire work that was already retired. Work ID: {work_id}"
            )

    def get_work_by_id(self, work_id: uuid.UUID) -> Optional[FullWork]:
        if work_id in self.assigned_work:
            return self.assigned_work[work_id]
        elif work_id in self.retired_work:
            logger.warning(f"{work_id} has already been retired")
            return None

    def update_analysis_by_work_id(
        self, work_id: uuid.UUID, analysis: List[Optional[Analysis]]
    ) -> bool:
        if work_id not in self.assigned_work:
            logger.error(f"Work ID {work_id} not in assigned work.")
            logger.error(self.assigned_work)

        game_length = len(analysis)
        completed_plys = sum([1 if ply else 0 for ply in analysis])

        self.assigned_analysis[work_id] = analysis

        if completed_plys == game_length:
            logger.info(f"All analysis complete for work ID {work_id}")
            assert work_id in self.assigned_analysis
            return True
        else:
            logger.info(
                f"Received progress report on {work_id}. {round(completed_plys / game_length * 100)}% complete."
            )

        return False

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

"""
{
  "work": {
    "type": "analysis",
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "level": 0
  },
  "game_id": "abcdefgh",
  "position": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
  "variant": "standard",
  "moves": "e2e4 c7c5 c2c4 b8c6 g1e2 g8f6 b1c3 c6b4 g2g3 b4d3",
  "nodes": 3500000,
  "skipPositions": [
    0
  ]
}
"""
