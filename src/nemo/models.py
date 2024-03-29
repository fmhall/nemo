from pydantic import BaseModel, Field
from typing import Dict, Optional, List, Any
from uuid import UUID


class Fishnet(BaseModel):
    version: str
    python: str
    apikey: str


class Stockfish(BaseModel):
    name: str
    options: Dict[str, str]


class Work(BaseModel):
    type: str
    id: UUID
    level: Optional[int] = None


class FullWork(BaseModel):
    work: Work
    game_id: Optional[str]
    position: str
    variant: str = "standard"
    moves: str
    nodes: Optional[int]
    skipPositions: List[int]
