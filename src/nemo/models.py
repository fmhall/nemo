from pydantic import BaseModel, Field
from typing import Dict, Optional, List, Any
from uuid import UUID
import uuid
import string
import random


def random_string(string_length=8):
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for _ in range(string_length))


class Fishnet(BaseModel):
    version: str
    python: str
    apikey: str


class Stockfish(BaseModel):
    name: str
    options: Dict[str, str]


class Work(BaseModel):
    type: str = "analysis"
    id: UUID = uuid.uuid4()
    level: Optional[int] = None


class FullWork(BaseModel):
    work: Work
    game_id: Optional[str] = random_string()
    position: str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    variant: str = "standard"
    moves: str
    nodes: Optional[int]
    skipPositions: List[int]


class Analysis(BaseModel):
    pv: Optional[str]
    seldepth: Optional[int]
    tbhits: Optional[int]
    depth: Optional[int]
    score: Optional[Any]
    time: Optional[int]
    nodes: Optional[int]
    nps: Optional[int]
    skipped: Optional[bool]


class Pgn_sub(BaseModel):
    pgn: str
    check_cloud: Optional[bool] = False
    pass
