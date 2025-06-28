import pygame
import json
import os
from typing import List, Dict, Tuple
from gfx import load_svg

WHITE = (248, 248, 248)
GREY = (60, 60, 60)
ACCENT = (255, 180, 0)

FONT_SIZE = 22
ICON_SIZE = 120
PADDING = 20


class PositionMenu:
    """Two-step GUI menu: choose category → choose position."""

    def __init__(self, screen: pygame.Surface, positions: List[Dict]):
        self.screen = screen
        self.positions = positions
        self.clock = pygame.time.Clock()
        pygame.font.init()
        self.font = pygame.font.Font(None, FONT_SIZE)

        # Build category list & icon mapping
        self.categories = {}
        for pos in positions:
            cat = pos["category"]
            icon = pos.get("icon", "icons/opening.svg")
            self.categories.setdefault(cat, icon)

        self.state = "cat"  # or "pos"
        self.selected_category = None
        self.running = True
        self.result = None

    # ---------------------------------------------------------------------
    def run(self):
        while self.running:
            self._handle_events()
            self._draw()
            pygame.display.flip()
            self.clock.tick(30)
        return self.result

    # ---------------------------------------------------------------------
    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if self.state == "pos":
                    self.state = "cat"
                else:
                    self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.state == "cat":
                    self._handle_cat_click(event.pos)
                else:
                    self._handle_pos_click(event.pos)

    # ---------------------------------------------------------------------
    def _draw(self):
        self.screen.fill(GREY)
        if self.state == "cat":
            self._draw_categories()
        else:
            self._draw_positions()

    # ---------------------------------------------------------------------
    def _draw_categories(self):
        cats = list(self.categories.items())
        cols = 3
        w, h = self.screen.get_size()
        col_w = (w - 2 * PADDING) // cols
        row_h = ICON_SIZE + 2 * PADDING + FONT_SIZE

        for idx, (cat, icon_path) in enumerate(cats):
            row = idx // cols
            col = idx % cols
            x = PADDING + col * col_w + (col_w - ICON_SIZE) // 2
            y = PADDING + row * row_h
            surf = load_svg(icon_path, ICON_SIZE)
            rect = pygame.Rect(x, y, ICON_SIZE, ICON_SIZE)
            self.screen.blit(surf, rect)
            # Text
            text_surface = self.font.render(cat, True, WHITE)
            tw = text_surface.get_width()
            self.screen.blit(text_surface, (x + (ICON_SIZE - tw) // 2, y + ICON_SIZE + 5))

    # ---------------------------------------------------------------------
    def _handle_cat_click(self, pos):
        cats = list(self.categories.items())
        cols = 3
        w, _ = self.screen.get_size()
        col_w = (w - 2 * PADDING) // cols
        row_h = ICON_SIZE + 2 * PADDING + FONT_SIZE
        for idx, (cat, _) in enumerate(cats):
            row = idx // cols
            col = idx % cols
            x = PADDING + col * col_w + (col_w - ICON_SIZE) // 2
            y = PADDING + row * row_h
            rect = pygame.Rect(x, y, ICON_SIZE, ICON_SIZE)
            if rect.collidepoint(pos):
                self.selected_category = cat
                self.state = "pos"
                return

    # ---------------------------------------------------------------------
    def _draw_positions(self):
        # Left side list
        filtered = [p for p in self.positions if p["category"] == self.selected_category]
        w, h = self.screen.get_size()
        list_width = w // 2
        pygame.draw.rect(self.screen, (30, 30, 30), (0, 0, list_width, h))
        y = PADDING
        for pos in filtered:
            line = f"{pos['id']:2d}. {pos['name']}"
            self.screen.blit(self.font.render(line, True, WHITE), (PADDING, y))
            y += FONT_SIZE + 10
        # Right side description placeholder
        self.screen.blit(self.font.render(self.selected_category, True, ACCENT), (list_width + PADDING, PADDING))
        self.screen.blit(self.font.render("Click a position in list…", True, WHITE), (list_width + PADDING, PADDING + 40))

    def _handle_pos_click(self, pos):
        filtered = [p for p in self.positions if p["category"] == self.selected_category]
        list_width = self.screen.get_width() // 2
        if pos[0] > list_width:
            return
        y = PADDING
        idx = (pos[1] - y) // (FONT_SIZE + 10)
        if 0 <= idx < len(filtered):
            self.result = filtered[idx]
            self.running = False 