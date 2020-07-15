from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from typing import Dict, List, Any, Optional
import requests
from nemo.models import Fishnet, Stockfish, FullWork, Analysis, Pgn_sub
from nemo.work_queue import work_queue
from nemo import utils
import uuid
import logging

logger = logging.getLogger(__name__)

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
    full_work = get_next_work_item(fishnet, stockfish)
    if not full_work:
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content={})
    return full_work


@app.post("/analysis/{work_id}", status_code=status.HTTP_202_ACCEPTED)
def post_analysis(
    work_id: uuid.UUID,
    fishnet: Fishnet,
    stockfish: Stockfish,
    analysis: Optional[List[Optional[Analysis]]],
):
    give_new_work = process_analysis(work_id, fishnet, stockfish, analysis)
    if give_new_work:
        full_work = get_next_work_item(fishnet, stockfish)
        if full_work:
            return full_work
        logger.warning("Work from queue was empty")

    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content={})


@app.post("/abort/{work_id}", status_code=status.HTTP_204_NO_CONTENT)
def abort(work_id: uuid.UUID, fishnet: Fishnet, stockfish: Stockfish):
    work = work_queue.get_work_by_id(work_id)
    logger.warning(f"Work ID {work_id} was forsaken, adding back to queue")
    work_queue.add_work_item(work)
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content={})


@app.post("/work", status_code=status.HTTP_202_ACCEPTED)
def post_work(full_work: FullWork):
    work_id = full_work.work.id
    if work_id in work_queue.assigned_analysis:
        if work_id in work_queue.retired_work:
            return JSONResponse(status_code=status.HTTP_200_OK, content={})
        return JSONResponse(status_code=status.HTTP_202_ACCEPTED, content={})

    work_queue.add_work_item(full_work)

    return JSONResponse(status_code=status.HTTP_201_CREATED, content={})


@app.get("/work/{game_id}", status_code=status.HTTP_200_OK)
def get_analysis(game_id: str):
    if game_id in work_queue.game_url_to_uuid:
        work_id = work_queue.game_url_to_uuid[game_id]
        if work_id in work_queue.assigned_analysis:
            return work_queue.assigned_analysis[work_id]
        else:
            logger.warning("Analysis not finished")
    else:
        logger.warning("Game ID not in game ID to work ID map")
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content={})


@app.post("/game", status_code=status.HTTP_202_ACCEPTED)
def post_game(pgn_sub: Pgn_sub):
    game = utils.pgn_to_game(pgn_sub.pgn)
    if game and pgn_sub.check_cloud:
        url = "https://lichess.org/api/cloud-eval"
        board = game.board()
        for move_num, move in enumerate(game.mainline_moves()):
            board.push(move)
            fen = board.fen()
            logger.debug(fen)
            response = requests.get(url, params={"fen": fen})
            if response.status_code == 200:
                logger.debug(response.json())
    else:
        logger.debug("Not checking cloud evals")

    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"pgn": str(game)})


def get_next_work_item(fishnet: Fishnet, stockfish: Stockfish) -> Optional[FullWork]:
    new_work = work_queue.get_next_work_item()
    if new_work:
        logger.debug(f"Giving next work item, ID: {new_work.work.id}")
    return new_work


def process_analysis(
    work_id: uuid.UUID,
    fishnet: Fishnet,
    stockfish: Stockfish,
    analysis: Optional[List[Optional[Analysis]]],
) -> bool:
    work = work_queue.get_work_by_id(work_id)
    if not analysis:
        logger.error(f"Work ID {work_id} had empty analysis, adding back to queue")
        work_queue.add_work_item(work)
    else:
        fully_analyzed = work_queue.update_analysis_by_work_id(work_id, analysis)
        if not fully_analyzed:
            # Dont give new work to the client until its finished
            return False
        work_queue.retire_work_item(work_id)
    # Give new work to the client
    return True
