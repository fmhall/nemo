import logging
import uuid
from typing import List, Optional

import requests
from fastapi import FastAPI, status, Response, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import json
from nemo import utils
from nemo.models import FullWork, Analysis, Pgn_sub, Move, FishnetDetails
from nemo.work_queue import work_queue

logger = logging.getLogger(__name__)

app = FastAPI()


# class async_iterator_wrapper:
#     def __init__(self, obj):
#         self._it = iter(obj)
#     def __aiter__(self):
#         return self
#     async def __anext__(self):
#         try:
#             value = next(self._it)
#         except StopIteration:
#             raise StopAsyncIteration
#         return value


# @app.middleware("http")
# async def log_request(request, call_next):
#     logger.info(f'{request.method} {request.url}')
#     logger.info(f'{await request.body()}')
#     logger.info("here")
#     response = await call_next(request)
#     logger.info("here2")
#     # Consuming FastAPI response and grabbing body here
#     # resp_body = [section async for section in response.__dict__['body_iterator']]
#     # # Repairing FastAPI response
#     # response.__setattr__('body_iterator', async_iterator_wrapper(resp_body))
#     #
#     # # Formatting response body for logging
#     # try:
#     #     resp_body = json.loads(resp_body[0].decode())
#     # except:
#     #     resp_body = str(resp_body)
#     # logger.info(f'Status code: {response.status_code}')
#     # logger.info(f'Response body: {resp_body}')
#     return response
"""
{
'fishnet': {
    'version': '2.2.7-dev', 
    'apikey': 'hello'
    }
}
"""


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/fishnet/acquire", status_code=status.HTTP_202_ACCEPTED, response_model=FullWork)
@app.exception_handler(RequestValidationError)
async def acquire(fishnet: FishnetDetails):
    logger.debug("Request for new work from {}".format(fishnet))
    full_work = get_next_work_item()
    if not full_work:
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)
    logger.info(full_work.dict())
    return JSONResponse(status_code=status.HTTP_202_ACCEPTED, content=full_work.dict())


@app.post("/fishnet/analysis/{work_id}", status_code=status.HTTP_202_ACCEPTED)
def post_analysis(
    work_id: uuid.UUID,
    analysis: Optional[List[Optional[Analysis]]],
):
    give_new_work = process_analysis(work_id, analysis)
    if give_new_work:
        full_work = get_next_work_item()
        if full_work:
            return full_work
        logger.warning("Work from queue was empty")

    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content={})


@app.post("/fishnet/move/{work_id}", status_code=status.HTTP_202_ACCEPTED)
def post_analysis(
    work_id: uuid.UUID, move: Optional[Move],
):
    # give_new_work = process_move(work_id, fishnet, move)

    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content={})


@app.post("/abort/{work_id}", status_code=status.HTTP_204_NO_CONTENT)
def abort(work_id: uuid.UUID):
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


# @app.get("/fishnet/status", status_code=status.HTTP_200_OK)
# def status_handler():
#     status_response = {
#         "analysis": {
#             "user": {
#                 "acquired": 0,
#                 "queued": 1,
#                 "oldest": 5
#             },
#             "system": {
#                 "acquired": 0,
#                 "queued": 12,
#                 "oldest": 12
#             }
#         }
#     }
#
#     return status_response


def get_next_work_item() -> Optional[FullWork]:
    new_work = work_queue.get_next_work_item()
    if new_work:
        logger.info(f"Giving next work item, ID: {new_work.work.id}")
    return new_work


def process_analysis(
    work_id: uuid.UUID,
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
