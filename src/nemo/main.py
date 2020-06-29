from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from typing import Dict, List, Any
from nemo.models import Fishnet, Stockfish, Work, FullWork, Analysis
from nemo.work_queue import work_queue
import uuid

app = FastAPI()

"""
{"fishnet": {
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
  }
}
"""


@app.post("/acquire", status_code=status.HTTP_202_ACCEPTED)
def acquire(fishnet: Fishnet, stockfish: Stockfish):
    full_work = get_work(fishnet, stockfish)
    if not full_work:
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content={})
    return full_work


@app.post("/analysis/{work_id}", status_code=status.HTTP_204_NO_CONTENT)
def post_analysis(
    work_id: str, fishnet: Fishnet, stockfish: Stockfish, analyses: List[Analysis]
):
    saved = process_analysis(analyses)
    full_work = None
    if not full_work:
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content={})
    return full_work


@app.post("/abort/{work_id}", status_code=status.HTTP_204_NO_CONTENT)
def abort(work_id: str, fishnet: Fishnet, stockfish: Stockfish):

    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content={})


@app.post("/games/{work_id}", status_code=status.HTTP_204_NO_CONTENT)
def abort(work_id: str, fishnet: Fishnet, stockfish: Stockfish):

    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content={})


def get_work(fishnet: Fishnet, stockfish: Stockfish) -> FullWork:

    return work_queue.get_next_work_item()


def process_analysis(analysis: List[Any]):
    saved: bool = True
    return saved
