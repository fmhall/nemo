import os
import json
import requests
from dotenv import load_dotenv
import logging
from fastapi.testclient import TestClient
from nemo.main import app
from nemo import utils

client = TestClient(app)

logger = logging.getLogger(__name__)
load_dotenv()
PLAYER = os.getenv("PLAYER")
URL = f"https://lichess.org/api/games/user/{PLAYER}"


def get_game_from_lichess() -> str:
    response = requests.get(URL, params={"max": 1, "analysed": False})
    return response.text


def test_post_game():

    data: str = get_game_from_lichess()
    logger.debug(data)
    r = client.post("/game", json={"pgn": "{" + data + "}", "check_cloud": False})
    logger.debug(r.text)
    assert r.status_code == 201
