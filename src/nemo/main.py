from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, Optional, List, Any


app = FastAPI()


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


"""
"fishnet": {
    "version": "1.15.7",
    "python": "2.7.11+",
    "apikey": "XXX"
  },
  "stockfish": {
    "name": "Stockfish 7 64",
    "options": {
      "hash": "256",
      "threads": "4"
    }
"""


# @app.get("/status")
# def read_root():
#     return {"Hello": "World"}


@app.post("/acquire", status_code=status.HTTP_202_ACCEPTED)
def acquire(fishnet: Fishnet, stockfish: Stockfish):
    full_work = get_work(fishnet, stockfish)
    if not full_work:
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content={})
    return full_work


@app.post("/analysis/{work_id}", status_code=status.HTTP_204_NO_CONTENT)
def post_analysis(
    work_id: str, fishnet: Fishnet, stockfish: Stockfish, analysis: List[Dict[str, Any]]
):

    saved = process_analysis(analysis)
    full_work = None
    if not full_work:
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content={})
    return full_work


@app.post("/abort/{work_id}", status_code=status.HTTP_204_NO_CONTENT)
def abort(work_id: str, fishnet: Fishnet, stockfish: Stockfish):

    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content={})


def get_work(fishnet: Fishnet, stockfish: Stockfish) -> FullWork:
    work = Work(work_type="analysis", work_id="work_id")
    print(work)
    response = FullWork(
        work={"id": work.work_id, "type": work.work_type},
        game_id="abcdefgh",
        position="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
        moves="e2e4 c7c5 c2c4 b8c6 g1e2 g8f6 b1c3 c6b4 g2g3 b4d3",
        nodes=3500000,
        skipPositions=[1, 4, 5],
    )
    return response


def process_analysis(analysis: List[Dict[str, str]]):
    saved: bool = True
    return saved
