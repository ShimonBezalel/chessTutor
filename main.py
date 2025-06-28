from __future__ import annotations
import sys
import random
import pygame
import chess
import os
from typing import Optional
import json
from menu import PositionMenu

# --- Constants --------------------------------------------------------------
BOARD_SIZE = 640  # Pixels (square board)
SQUARE_SIZE = BOARD_SIZE // 8
FPS = 30

LIGHT_COLOR = (240, 217, 181)  # Light squares
DARK_COLOR = (181, 136, 99)    # Dark squares
SELECTED_COLOR = (246, 246, 105)
MOVE_DOT_COLOR = (106, 246, 105)
STATUS_BAR_HEIGHT = 0  # No status bar now

# Piece drawing colors
WHITE_PIECE = (248, 248, 248)
BLACK_PIECE = (32, 32, 32)
OUTLINE = (20, 20, 20)


# --- Helper functions -------------------------------------------------------

def square_from_mouse(pos):
    """Convert (x, y) in pixels to a python-chess square index."""
    x, y = pos
    if y >= BOARD_SIZE:
        return None
    file_ = x // SQUARE_SIZE  # 0-7
    rank_ = y // SQUARE_SIZE  # 0 (top) – 7 (bottom)
    return chess.square(file_, 7 - rank_)  # Flip so White is at bottom.


def generate_piece_images(square_size: int):
    """Return dict mapping python-chess piece symbols to pygame.Surface.

    The drawings purposely avoid fonts and instead approximate classic Staunton
    silhouettes with basic geometry (rectangles, circles, polygons).  Each
    piece is first drawn in `OUTLINE` a few pixels larger, then filled with the
    inner `WHITE_PIECE` / `BLACK_PIECE` colour so we get a crisp border.
    """

    images: dict[str, pygame.Surface] = {}
    s = square_size
    stroke = max(2, s // 28)  # thickness of black outline

    def o(val: float) -> int:
        """Scale helper -> int pixel from 0-1 proportion."""
        return int(val * s)

    for symbol in "PNBRQKpnbrqk":
        surf = pygame.Surface((s, s), pygame.SRCALPHA)
        col = WHITE_PIECE if symbol.isupper() else BLACK_PIECE

        def draw_circle(center, rad):
            pygame.draw.circle(surf, OUTLINE, center, rad + stroke)
            pygame.draw.circle(surf, col, center, rad)

        def draw_rect(rect):
            out = pygame.Rect(rect).inflate(stroke * 2, stroke * 2)
            pygame.draw.rect(surf, OUTLINE, out)
            pygame.draw.rect(surf, col, rect)

        def draw_polygon(points):
            pygame.draw.polygon(surf, OUTLINE, points, 0)
            # shrink polygon slightly toward centroid for fill
            shrink_pts = [(
                (p[0] + (s/2 - p[0]) * stroke / max(s*0.5,1)),
                (p[1] + (s/2 - p[1]) * stroke / max(s*0.5,1))
            ) for p in points]
            pygame.draw.polygon(surf, col, shrink_pts, 0)

        up = symbol.upper()

        if up == "P":  # Pawn – kept small & simple
            # Head
            draw_circle((o(0.5), o(0.33)), o(0.12))
            # Neck
            draw_rect(pygame.Rect(o(0.46), o(0.37), o(0.08), o(0.03)))
            # Body
            draw_rect(pygame.Rect(o(0.4), o(0.40), o(0.2), o(0.18)))
            # Base tiers
            draw_rect(pygame.Rect(o(0.32), o(0.59), o(0.36), o(0.05)))
            draw_rect(pygame.Rect(o(0.26), o(0.67), o(0.48), o(0.05)))

        elif up == "R":  # Rook – chunky tower & bold battlements
            # Body
            draw_rect(pygame.Rect(o(0.30), o(0.28), o(0.40), o(0.48)))
            # Arrow-slit windows
            draw_rect(pygame.Rect(o(0.46), o(0.40), o(0.04), o(0.14)))
            # Battlements (5 blocks)
            cren_w = o(0.08)
            y_top = o(0.18)
            for i in range(5):
                x = o(0.30) + i * cren_w
                draw_rect(pygame.Rect(x, y_top, cren_w - stroke, o(0.09)))
            # Base
            draw_rect(pygame.Rect(o(0.24), o(0.78), o(0.52), o(0.05)))
            draw_rect(pygame.Rect(o(0.18), o(0.85), o(0.64), o(0.05)))

        elif up == "N":  # Knight – clearer horse profile
            pts = [
                (o(0.28), o(0.82)),  # bottom-left
                (o(0.46), o(0.32)),
                (o(0.42), o(0.18)),
                (o(0.58), o(0.08)),  # muzzle tip
                (o(0.74), o(0.28)),  # ear tip
                (o(0.60), o(0.38)),
                (o(0.74), o(0.58)),  # neck curve
                (o(0.52), o(0.74)),
            ]
            draw_polygon(pts)
            draw_rect(pygame.Rect(o(0.22), o(0.82), o(0.56), o(0.05)))

        elif up == "B":  # Bishop – slender with pronounced mitre
            # Mitre head
            draw_circle((o(0.5), o(0.25)), o(0.15))
            # Vertical slit – draw thin transparent line
            pygame.draw.line(surf, (0, 0, 0, 0), (o(0.5), o(0.12)), (o(0.5), o(0.38)), stroke)
            # Shoulders
            draw_rect(pygame.Rect(o(0.38), o(0.36), o(0.24), o(0.16)))
            # Body taper – trapezoid simulated with polygon
            draw_polygon([
                (o(0.36), o(0.54)), (o(0.64), o(0.54)), (o(0.58), o(0.64)), (o(0.42), o(0.64))
            ])
            # Base
            draw_rect(pygame.Rect(o(0.3), o(0.66), o(0.4), o(0.07)))
            draw_rect(pygame.Rect(o(0.24), o(0.75), o(0.52), o(0.05)))

        elif up == "Q":  # Queen – distinct crown & flowing gown
            # Crown pearls
            for x in [0.3, 0.38, 0.46, 0.54, 0.62, 0.70]:
                draw_circle((o(x), o(0.14)), o(0.05))
            # Crown band (double)
            draw_rect(pygame.Rect(o(0.32), o(0.19), o(0.36), o(0.03)))
            draw_rect(pygame.Rect(o(0.34), o(0.23), o(0.32), o(0.03)))
            # Upper body orb
            draw_circle((o(0.5), o(0.30)), o(0.14))
            # Braids (three beads down each side)
            braid_xs = [o(0.3), o(0.7)]
            for bx in braid_xs:
                for y_frac in [0.24, 0.32, 0.40]:
                    draw_circle((bx, o(y_frac)), o(0.04))
            # Lower gown (flare)
            draw_polygon([
                (o(0.3), o(0.40)), (o(0.70), o(0.40)), (o(0.58), o(0.65)), (o(0.42), o(0.65))
            ])
            # Base
            draw_rect(pygame.Rect(o(0.28), o(0.66), o(0.44), o(0.06)))
            draw_rect(pygame.Rect(o(0.2), o(0.74), o(0.6), o(0.05)))

        elif up == "K":  # King – tallest, broad base
            # Cross top (thicker)
            draw_rect(pygame.Rect(o(0.47), o(0.05), o(0.06), o(0.15)))
            draw_rect(pygame.Rect(o(0.43), o(0.11), o(0.14), o(0.05)))
            # Head orb
            draw_circle((o(0.5), o(0.26)), o(0.16))
            # Body (longer than Queen)
            draw_rect(pygame.Rect(o(0.34), o(0.34), o(0.32), o(0.38)))
            # Base tiers
            draw_rect(pygame.Rect(o(0.28), o(0.72), o(0.44), o(0.05)))
            draw_rect(pygame.Rect(o(0.22), o(0.80), o(0.56), o(0.05)))

        images[symbol] = surf

    return images


def draw_board(screen, board, piece_images: dict[str, pygame.Surface], selected_sq=None, legal_dests=set()):
    """Render board, pieces, and highlights using pre-generated images."""
    # Squares
    for rank in range(8):
        for file in range(8):
            rect = pygame.Rect(
                file * SQUARE_SIZE, rank * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE
            )
            color = LIGHT_COLOR if (file + rank) % 2 == 0 else DARK_COLOR
            pygame.draw.rect(screen, color, rect)

            square = chess.square(file, 7 - rank)
            # Highlights
            if square == selected_sq:
                pygame.draw.rect(screen, SELECTED_COLOR, rect)
            if square in legal_dests:
                center = rect.center
                pygame.draw.circle(screen, MOVE_DOT_COLOR, center, 10)

            # Pieces
            piece = board.piece_at(square)
            if piece:
                img = piece_images[piece.symbol()]
                img_rect = img.get_rect(center=rect.center)
                screen.blit(img, img_rect)


# --- AI helper --------------------------------------------------------------

PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 0,
}


def evaluate_material(board: chess.Board) -> int:
    """Simple material count from White perspective (centipawns)."""
    score = 0
    for piece_type in PIECE_VALUES:
        score += PIECE_VALUES[piece_type] * (
            len(board.pieces(piece_type, chess.WHITE)) - len(board.pieces(piece_type, chess.BLACK))
        )
    return score


def negamax(board: chess.Board, depth: int, alpha: int, beta: int) -> int:
    """Negamax search with alpha-beta pruning."""
    if depth == 0 or board.is_game_over():
        eval_score = evaluate_material(board)
        return eval_score if board.turn == chess.WHITE else -eval_score

    max_eval = -10_000
    for move in board.legal_moves:
        board.push(move)
        score = -negamax(board, depth - 1, -beta, -alpha)
        board.pop()
        if score > max_eval:
            max_eval = score
        alpha = max(alpha, score)
        if alpha >= beta:
            break
    return max_eval


# Try to load Stockfish: expects binary named "stockfish" in PATH.
try:
    from chess.engine import SimpleEngine, Limit
    STOCKFISH_PATH = os.getenv("STOCKFISH_PATH", "stockfish")
    _engine: Optional["SimpleEngine"] = SimpleEngine.popen_uci(STOCKFISH_PATH)
except Exception:
    _engine = None


def choose_ai_move(board: chess.Board, depth: int = 2) -> chess.Move:
    """Return AI move. Use Stockfish if available, otherwise fallback to material search."""

    if _engine:
        try:
            # Use skill level 5 (0-20). You can raise for harder play.
            _engine.configure({"Skill Level": 10})
            result = _engine.play(board, Limit(depth=depth + 6))  # deeper than DIY search
            return result.move
        except Exception:
            pass  # If engine fails, fall back

    # Fallback minimax
    best_move = None
    best_score = -10_000
    for move in board.legal_moves:
        board.push(move)
        score = -negamax(board, depth - 1, -10_000, 10_000)
        board.pop()
        if score > best_score:
            best_score = score
            best_move = move
    return best_move if best_move else random.choice(list(board.legal_moves))


# --- Main game loop ---------------------------------------------------------

def main():
    # --- Load start positions ---
    with open(os.path.join(os.path.dirname(__file__), "start_positions.json"), "r") as f:
        START_POSITIONS = json.load(f)

    # Open graphical menu before game starts
    pygame.init()
    screen = pygame.display.set_mode((BOARD_SIZE, BOARD_SIZE + STATUS_BAR_HEIGHT))
    pygame.display.set_caption("Chess Tutor – MVP")

    piece_images = generate_piece_images(SQUARE_SIZE)
    clock = pygame.time.Clock()

    board = chess.Board()
    menu = PositionMenu(screen, START_POSITIONS)
    selected = menu.run()

    if selected:
        board.set_fen(selected["fen"])
        board.clear_stack()
        pygame.display.set_caption(f"Chess Tutor – {selected['name']}")

    selected_sq = None
    legal_dests = set()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1  # Left click
                and not board.is_game_over()
            ):
                sq = square_from_mouse(event.pos)
                if sq is None:
                    continue

                # 1) Selecting a piece
                if selected_sq is None:
                    piece = board.piece_at(sq)
                    if piece and piece.color == chess.WHITE and board.turn == chess.WHITE:
                        selected_sq = sq
                        legal_dests = {
                            m.to_square for m in board.legal_moves if m.from_square == sq
                        }
                # 2) Moving the previously selected piece
                else:
                    if sq in legal_dests:
                        move = chess.Move(selected_sq, sq)
                        # Simple promotion to queen for pawns reaching the back rank.
                        if (
                            board.piece_type_at(selected_sq) == chess.PAWN
                            and chess.square_rank(sq) in (0, 7)
                        ):
                            move.promotion = chess.QUEEN
                        if move in board.legal_moves:
                            board.push(move)
                            selected_sq = None
                            legal_dests = set()

                            # --- Computer move (very weak) ---
                            if not board.is_game_over():
                                comp_move = choose_ai_move(board, depth=2)
                                board.push(comp_move)
                    else:
                        # Clicked elsewhere – reset selection
                        selected_sq = None
                        legal_dests = set()

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_F2:
                # Open menu mid-game
                menu = PositionMenu(screen, START_POSITIONS)
                res = menu.run()
                if res:
                    board.set_fen(res["fen"])
                    board.clear_stack()
                    selected_sq = None
                    legal_dests = set()
                    pygame.display.set_caption(f"Chess Tutor – {res['name']}")

        # Draw everything
        screen.fill((0, 0, 0))
        draw_board(screen, board, piece_images, selected_sq, legal_dests)

        # Caption instead of status bar (avoids fonts)
        if board.is_game_over():
            if board.is_checkmate():
                caption = "You Win!" if board.turn == chess.BLACK else "You Lose!"
            else:
                caption = "Draw: " + board.result()
        else:
            caption = "Your move" if board.turn == chess.WHITE else "Computer's move"
        pygame.display.set_caption(f"Chess Tutor – MVP  |  {caption}")

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    if _engine:
        _engine.quit()
    sys.exit()


if __name__ == "__main__":
    main() 