from __future__ import annotations
import math
import random
import pygame
import pygame.gfxdraw
from quoridor import constants as C


class BoardView:
    def __init__(self):
        pygame.font.init()
        self.font_coord = pygame.font.SysFont("consolas", 15, bold=True)
        self.pad = 12
        self.board_surf = self._build_board()

    @staticmethod
    def cell_rect(row: int, col: int) -> pygame.Rect:
        x = C.BOARD_OFFSET_X + col * C.STEP
        y = C.BOARD_OFFSET_Y + row * C.STEP
        return pygame.Rect(x, y, C.CELL, C.CELL)

    @staticmethod
    def pixel_to_cell(mx: int, my: int) -> tuple[int, int] | None:
        for r in range(C.BOARD_SIZE):
            for c in range(C.BOARD_SIZE):
                if BoardView.cell_rect(r, c).collidepoint(mx, my):
                    return r, c
        return None

    def _draw_vector_rune(self, surf: pygame.Surface, cx: int, cy: int, rune_type: int):
        color = C.C_RUNE_COLOR
        thick = 2
        s = 8
        if rune_type == 0:
            pygame.draw.line(surf, color, (cx, cy - s), (cx, cy + s), thick)
            pygame.draw.line(surf, color, (cx, cy - s + 3), (cx + s, cy - s + 7), thick)
            pygame.draw.line(surf, color, (cx, cy - 2), (cx + s, cy + 2), thick)
        elif rune_type == 1:
            pygame.draw.line(surf, color, (cx, cy - s), (cx, cy + s), thick)
            pygame.draw.line(surf, color, (cx, cy - s), (cx - s, cy - s + 5), thick)
            pygame.draw.line(surf, color, (cx, cy - s), (cx + s, cy - s + 5), thick)
        elif rune_type == 2:
            pts = [(cx, cy - s), (cx + s - 2, cy), (cx, cy + s), (cx - s + 2, cy)]
            pygame.draw.lines(surf, color, True, pts, thick)
        elif rune_type == 3:
            pygame.draw.line(surf, color, (cx, cy - s), (cx, cy + s), thick)
            pygame.draw.line(surf, color, (cx - s, cy + s // 2), (cx + s, cy - s // 2), thick)
        elif rune_type == 4:
            pts = [(cx - s + 2, cy - s), (cx + s - 2, cy - s // 3), (cx - s + 2, cy + s // 3), (cx + s - 2, cy + s)]
            pygame.draw.lines(surf, color, False, pts, thick)

    def _build_board(self) -> pygame.Surface:
        w = C.BOARD_PX + self.pad * 2
        h = C.BOARD_PX + self.pad * 2
        s = pygame.Surface((w, h), pygame.SRCALPHA)

        outer = pygame.Rect(0, 0, w, h)
        pygame.draw.rect(s, (18, 22, 36), outer, border_radius=8)
        pygame.draw.rect(s, (50, 65, 95), outer, 2, border_radius=8)

        inner = pygame.Rect(self.pad - 4, self.pad - 4, C.BOARD_PX + 8, C.BOARD_PX + 8)
        pygame.draw.rect(s, (16, 20, 32), inner, border_radius=6)

        rng = random.Random(99)

        for r in range(C.BOARD_SIZE):
            for c in range(C.BOARD_SIZE):
                x = self.pad + c * C.STEP
                y = self.pad + r * C.STEP
                rect = pygame.Rect(x, y, C.CELL, C.CELL)

                shade = rng.randint(-4, 4)
                base = tuple(max(0, min(255, v + shade)) for v in C.C_STONE_MID)
                pygame.draw.rect(s, base, rect, border_radius=3)

                for _ in range(2):
                    lx1 = x + rng.randint(5, C.CELL - 9)
                    ly1 = y + rng.randint(5, C.CELL - 9)
                    lx2 = lx1 + rng.randint(-7, 7)
                    ly2 = ly1 + rng.randint(-7, 7)
                    pygame.draw.line(s, C.C_STONE_LINE, (lx1, ly1), (lx2, ly2), 1)

                if rng.random() < 0.28:
                    rtype = rng.randint(0, 4)
                    self._draw_vector_rune(s, x + C.CELL // 2, y + C.CELL // 2, rtype)

                pygame.draw.rect(s, C.C_STONE_LINE, rect, 1, border_radius=3)

        return s

    def draw_base(self, surf: pygame.Surface):
        bx = C.BOARD_OFFSET_X - self.pad
        by = C.BOARD_OFFSET_Y - self.pad
        surf.blit(self.board_surf, (bx, by))

    def draw_coordinates(self, surf: pygame.Surface):
        cols = "ABCDEFGHI"
        for i in range(C.BOARD_SIZE):
            lx = C.BOARD_OFFSET_X + i * C.STEP + C.CELL // 2
            ly = C.BOARD_OFFSET_Y - 18
            t_shadow = self.font_coord.render(cols[i], True, (10, 15, 30))
            t = self.font_coord.render(cols[i], True, C.C_COORD_COLOR)
            surf.blit(t_shadow, t_shadow.get_rect(center=(lx + 1, ly + 1)))
            surf.blit(t, t.get_rect(center=(lx, ly)))

            nx = C.BOARD_OFFSET_X - 18
            ny = C.BOARD_OFFSET_Y + i * C.STEP + C.CELL // 2
            n_shadow = self.font_coord.render(str(9 - i), True, (10, 15, 30))
            n = self.font_coord.render(str(9 - i), True, C.C_COORD_COLOR)
            surf.blit(n_shadow, n_shadow.get_rect(center=(nx + 1, ny + 1)))
            surf.blit(n, n.get_rect(center=(nx, ny)))

    def draw_goal_glow(self, surf: pygame.Surface, tick: float):
        pulse = 0.5 + 0.5 * math.sin(tick * 3)
        rows_data = [
            (0, C.C_GOAL_P1_GLOW, C.C_GOAL_P1_LINE),
            (C.BOARD_SIZE - 1, C.C_GOAL_P2_GLOW, C.C_GOAL_P2_LINE),
        ]
        for row, glow_c, line_c in rows_data:
            x = C.BOARD_OFFSET_X
            y = C.BOARD_OFFSET_Y + row * C.STEP

            for c in range(C.BOARD_SIZE):
                rect = self.cell_rect(row, c)
                s = pygame.Surface((C.CELL, C.CELL), pygame.SRCALPHA)
                alpha = int(glow_c[3] * (0.7 + 0.3 * pulse))
                s.fill((*glow_c[:3], alpha))
                surf.blit(s, rect.topleft)

            lw = C.BOARD_PX
            line_y = y + (0 if row == 0 else C.CELL)
            for thickness, alpha in ((6, 45), (3, 110), (1, 210)):
                ls = pygame.Surface((lw, thickness), pygame.SRCALPHA)
                ls.fill((*line_c[:3], int(alpha * (0.8 + 0.2 * pulse))))
                surf.blit(ls, (x, line_y - thickness // 2))

    def draw_paths(self, surf: pygame.Surface, p0: list, p1: list):
        for path, color in ((p0, C.C_P1), (p1, C.C_P2)):
            for i, (r, c) in enumerate(path[1:-1], 1):
                rect = self.cell_rect(r, c)
                s = pygame.Surface((C.CELL, C.CELL), pygame.SRCALPHA)
                alpha = max(10, 32 - i * 3)
                s.fill((*color, alpha))
                surf.blit(s, rect.topleft)

    def draw_valid_moves(self, surf: pygame.Surface, moves: list, mode: str, tick: float):
        if mode != C.MODE_MOVE:
            return
        pulse = 0.5 + 0.5 * math.sin(tick * 4)
        for r, c in moves:
            rect = self.cell_rect(r, c)
            s = pygame.Surface((C.CELL, C.CELL), pygame.SRCALPHA)
            s.fill((*C.C_CELL_VALID[:3], int(C.C_CELL_VALID[3] * (0.7 + 0.3 * pulse))))
            surf.blit(s, rect.topleft)
            pygame.draw.rect(surf, (*C.C_CELL_VALID_DOT, 210), rect, 2, border_radius=3)
            cx, cy = rect.centerx, rect.centery
            dot_r = int(6 + 2 * pulse)
            pygame.gfxdraw.aacircle(surf, cx, cy, dot_r, (*C.C_CELL_VALID_DOT, 190))
            pygame.gfxdraw.filled_circle(surf, cx, cy, dot_r, (*C.C_CELL_VALID_DOT, 190))
            pygame.gfxdraw.aacircle(surf, cx, cy, max(2, dot_r - 3), (255, 255, 255, 230))
            pygame.gfxdraw.filled_circle(surf, cx, cy, max(2, dot_r - 3), (255, 255, 255, 230))

    def draw_hover(self, surf: pygame.Surface, cell: tuple[int, int] | None, mode: str):
        if cell is None or mode != C.MODE_MOVE:
            return
        r, c = cell
        rect = self.cell_rect(r, c)
        s = pygame.Surface((C.CELL, C.CELL), pygame.SRCALPHA)
        s.fill((*C.C_CELL_HOVER[:3], C.C_CELL_HOVER[3]))
        surf.blit(s, rect.topleft)
        pygame.draw.rect(surf, (130, 190, 255, 170), rect, 2, border_radius=3)
