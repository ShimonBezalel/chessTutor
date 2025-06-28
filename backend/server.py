from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import chess
import json
import os

app = FastAPI(title="ChessTutor API", version="0.1")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Load start positions once at boot
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
with open(os.path.join(BASE_DIR, "start_positions.json"), "r") as f:
    START_POSITIONS = json.load(f)


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
    return {
        "ok": True,
        "fen": board.fen(),
        "legal_moves": [m.uci() for m in board.legal_moves]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.server:app", host="0.0.0.0", port=8000, reload=True) 