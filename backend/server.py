from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import chess
import json
import os
import random
from typing import Optional
from chess.engine import SimpleEngine, Limit

app = FastAPI(title="ChessTutor API", version="0.1")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Load start positions once at boot
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
with open(os.path.join(BASE_DIR, "start_positions.json"), "r") as f:
    START_POSITIONS = json.load(f)

# --- Simple AI (material count depth-2) -----------------------------

PIECE_VALUES = {chess.PAWN: 100, chess.KNIGHT: 320, chess.BISHOP: 330, chess.ROOK: 500, chess.QUEEN: 900, chess.KING: 0}


def eval_material(board: chess.Board) -> int:
    score = 0
    for pt, val in PIECE_VALUES.items():
        score += val * (len(board.pieces(pt, chess.WHITE)) - len(board.pieces(pt, chess.BLACK)))
    return score


def negamax(board: chess.Board, depth: int, alpha: int, beta: int) -> int:
    if depth == 0 or board.is_game_over():
        ev = eval_material(board)
        return ev if board.turn == chess.WHITE else -ev
    best = -10_000
    for mv in board.legal_moves:
        board.push(mv)
        score = -negamax(board, depth - 1, -beta, -alpha)
        board.pop()
        if score > best:
            best = score
        alpha = max(alpha, score)
        if alpha >= beta:
            break
    return best


# ---- Stockfish integration ---------------------------------------------

STOCKFISH_PATH = os.getenv("STOCKFISH_PATH", "stockfish")
try:
    ENGINE: Optional[SimpleEngine] = SimpleEngine.popen_uci(STOCKFISH_PATH)
    ENGINE.configure({"Skill Level": int(os.getenv("STOCKFISH_SKILL", "8"))})  # 0–20
except Exception:
    ENGINE = None


def choose_ai_move(board: chess.Board, depth: int = 2) -> chess.Move:
    """Return Stockfish move if engine available, else fallback minimax."""
    if ENGINE and not board.is_variant_end():
        try:
            result = ENGINE.play(board, Limit(depth=depth + 8))  # deeper search = stronger
            return result.move
        except Exception:
            pass  # fall back if engine errors

    # Fallback minimax
    best_move = None
    best_score = -10_000
    for mv in board.legal_moves:
        board.push(mv)
        score = -negamax(board, depth - 1, -10_000, 10_000)
        board.pop()
        if score > best_score:
            best_score = score
            best_move = mv
    return best_move or random.choice(list(board.legal_moves))


@app.get("/api/positions")
async def get_positions():
    """Return full list of curated starting positions."""
    return START_POSITIONS


@app.post("/api/move")
async def make_move(payload: dict):
    """Validate and apply a move.

    Payload JSON:
    {
        "fen": "...",
        "move": "e2e4"   # UCI
    }
    Returns new FEN, legality flag and list of legal moves for next player.
    """
    fen = payload.get("fen")
    uci = payload.get("move")
    if not fen or not uci:
        raise HTTPException(status_code=400, detail="fen and move required")

    try:
        board = chess.Board(fen)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid FEN: {exc}")

    try:
        move = chess.Move.from_uci(uci)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UCI move string")

    if move not in board.legal_moves:
        return {"ok": False, "fen": fen, "legal_moves": [m.uci() for m in board.legal_moves]}

    board.push(move)

    # AI reply if game not over
    ai_move = None
    if not board.is_game_over():
        ai_move = choose_ai_move(board)
        board.push(ai_move)

    return {
        "ok": True,
        "fen": board.fen(),
        "ai_move": ai_move.uci() if ai_move else None,
        "legal_moves": [m.uci() for m in board.legal_moves],
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.server:app", host="0.0.0.0", port=8000, reload=True)

# Gracefully close engine on exit
import atexit

if ENGINE:
    atexit.register(ENGINE.quit) 