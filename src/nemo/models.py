from pydantic import BaseModel, Field
from typing import Dict, Optional, List, Any


class Fishnet(BaseModel):
    version: str
    python: str
    apikey: str


class Stockfish(BaseModel):
    name: str
    options: Dict[str, str]


class Work(BaseModel):
    work_type: str
    work_id: str
    level: Optional[int] = None


class FullWork(BaseModel):
    work: Dict[str, str]
    game_id: Optional[str]
    position: str
    variant: str = "standard"
    moves: str
    nodes: Optional[int]
    skipPositions: List[int]