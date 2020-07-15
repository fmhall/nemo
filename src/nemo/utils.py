import chess.pgn
import logging
import io

logger = logging.getLogger(__name__)


def pgn_to_game(pgn: str):
    f_pgn = io.StringIO(pgn)
    game = chess.pgn.read_game(f_pgn)
    logger.info(game)

    return game
