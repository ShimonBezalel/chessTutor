from __future__ import annotations
import sys
import random
import pygame
import chess

# --- Constants --------------------------------------------------------------
BOARD_SIZE = 640  # Pixels (square board)
SQUARE_SIZE = BOARD_SIZE // 8
FPS = 30

LIGHT_COLOR = (240, 217, 181)  # Light squares
DARK_COLOR = (181, 136, 99)    # Dark squares
SELECTED_COLOR = (246, 246, 105)
MOVE_DOT_COLOR = (106, 246, 105)
STATUS_BAR_HEIGHT = 40

# Unicode pieces for quick, asset-free rendering
UNICODE_PIECES = {
    'P': '♙', 'N': '♘', 'B': '♗', 'R': '♖', 'Q': '♕', 'K': '♔',
    'p': '♟', 'n': '♞', 'b': '♝', 'r': '♜', 'q': '♛', 'k': '♚'
}


# --- Helper functions -------------------------------------------------------

def load_piece_font(size: int) -> pygame.font.Font:
    """Return a font that contains the Unicode chess piece glyphs."""
    candidates = [
        "DejaVu Sans", "Arial Unicode MS", "Symbola", "FreeSerif", None
    ]  # The final None picks pygame's default font.
    for name in candidates:
        try:
            return pygame.font.SysFont(name, size)
        except Exception:
            continue
    raise RuntimeError("No usable font found for chess pieces")


def square_from_mouse(pos):
    """Convert (x, y) in pixels to a python-chess square index."""
    x, y = pos
    if y >= BOARD_SIZE:
        return None
    file_ = x // SQUARE_SIZE  # 0-7
    rank_ = y // SQUARE_SIZE  # 0 (top) – 7 (bottom)
    return chess.square(file_, 7 - rank_)  # Flip so White is at bottom.


def draw_board(screen, board, piece_font, selected_sq=None, legal_dests=set()):
    """Render board, pieces, and highlights."""
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
                glyph = UNICODE_PIECES[piece.symbol()]
                text_surface = piece_font.render(glyph, True, (0, 0, 0))
                text_rect = text_surface.get_rect(center=rect.center)
                screen.blit(text_surface, text_rect)


# --- Main game loop ---------------------------------------------------------

def main():
    pygame.init()
    screen = pygame.display.set_mode((BOARD_SIZE, BOARD_SIZE + STATUS_BAR_HEIGHT))
    pygame.display.set_caption("Chess Tutor – MVP")

    piece_font = load_piece_font(SQUARE_SIZE)
    status_font = pygame.font.SysFont(None, 24)
    clock = pygame.time.Clock()

    board = chess.Board()

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
                                comp_move = random.choice(list(board.legal_moves))
                                board.push(comp_move)
                    else:
                        # Clicked elsewhere – reset selection
                        selected_sq = None
                        legal_dests = set()

        # Draw everything
        screen.fill((0, 0, 0))
        draw_board(screen, board, piece_font, selected_sq, legal_dests)

        # Status bar
        status_text = ""
        if board.is_game_over():
            if board.is_checkmate():
                status_text = "You Win!" if board.turn == chess.BLACK else "You Lose!"
            else:
                status_text = "Draw: " + board.result()
        else:
            status_text = "Your move" if board.turn == chess.WHITE else "Computer's move"
        status_surface = status_font.render(status_text, True, (0, 0, 0))
        screen.blit(status_surface, (10, BOARD_SIZE + 10))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main() 