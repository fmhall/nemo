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
    apikey: str


class FishnetDetails(BaseModel):
    fishnet: Fishnet


class Stockfish(BaseModel):
    name: str
    options: Dict[str, str]


class Nodes(BaseModel):
    nnue: int
    classical: int


class Work(BaseModel):
    type: str = "analysis"
    id: str = uuid.uuid4().hex
    nodes: Nodes


class FullWork(BaseModel):
    work: Work
    game_id: Optional[str] = random_string()
    position: str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    variant: str = "standard"
    moves: str
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


class Move(BaseModel):
    bestmove: Optional[str]


class Pgn_sub(BaseModel):
    pgn: str
    check_cloud: Optional[bool] = False
    pass
