from typing import Dict

from fastapi.testclient import TestClient

from nemo.main import app

client = TestClient(app)


def test_acquire():
    data = {
        "fishnet": {"version": "1.15.7", "python": "2.7.11+", "apikey": "XXX"},
        "stockfish": {
            "name": "Stockfish 7 64",
            "options": {"hash": "256", "threads": "4"},
        },
    }
    r = client.post("/acquire", json=data,)
    response = r.json()
    assert r.status_code == 202
    assert "work" in response

    r2 = client.post("/acquire", json=data,)
    response = r2.json()
    assert r2.status_code == 204
    assert "work" not in response
