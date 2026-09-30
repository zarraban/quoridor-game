from __future__ import annotations
import math
import pygame
import pygame.gfxdraw
from quoridor import constants as C
from quoridor.board_view import BoardView


class WallView:
    @staticmethod
    def wall_h_rect(r: int, c: int) -> pygame.Rect:
        x = C.BOARD_OFFSET_X + c * C.STEP
        y = C.BOARD_OFFSET_Y + (r + 1) * C.STEP - C.GAP
        return pygame.Rect(x, y, 2 * C.CELL + C.GAP, C.GAP)

    @staticmethod
    def wall_v_rect(r: int, c: int) -> pygame.Rect:
        x = C.BOARD_OFFSET_X + (c + 1) * C.STEP - C.GAP
        y = C.BOARD_OFFSET_Y + r * C.STEP
        return pygame.Rect(x, y, C.GAP, 2 * C.CELL + C.GAP)

    @staticmethod
    def pixel_to_wall_slot(mx: int, my: int, horizontal: bool) -> tuple[int, int] | None:
        bx = mx - C.BOARD_OFFSET_X
        by = my - C.BOARD_OFFSET_Y
        if not (-C.GAP <= bx <= C.BOARD_PX + C.GAP and -C.GAP <= by <= C.BOARD_PX + C.GAP):
            return None
        if horizontal:
            r = int((by - C.CELL) // C.STEP)
            c = int(bx // C.STEP)
            if 0 <= r < C.BOARD_SIZE - 1 and 0 <= c < C.BOARD_SIZE - 1:
                return r, c
        else:
            c = int((bx - C.CELL) // C.STEP)
            r = int(by // C.STEP)
            if 0 <= r < C.BOARD_SIZE - 1 and 0 <= c < C.BOARD_SIZE - 1:
                return r, c
        return None

    def draw_placed_walls(self, surf: pygame.Surface, h_walls: set, v_walls: set):
        for r, c in h_walls:
            self._draw_fancy_wall(surf, self.wall_h_rect(r, c), horizontal=True)
        for r, c in v_walls:
            self._draw_fancy_wall(surf, self.wall_v_rect(r, c), horizontal=False)

    def _draw_fancy_wall(self, surf: pygame.Surface, rect: pygame.Rect, horizontal: bool):
        glow_color = C.C_WALL_BLUE

        for i in range(9, 0, -1):
            exp = rect.inflate(i * 2, i * 2)
            gs = pygame.Surface(exp.size, pygame.SRCALPHA)
            alpha = int(48 * (i / 9))
            pygame.draw.rect(gs, (*glow_color, alpha), gs.get_rect(), border_radius=3 + i)
            surf.blit(gs, exp.topleft)

        wall_surf = pygame.Surface(rect.size, pygame.SRCALPHA)
        wall_surf.fill((*glow_color, 85))
        surf.blit(wall_surf, rect.topleft)
        pygame.draw.rect(surf, glow_color, rect, 2, border_radius=3)

        if horizontal:
            cy = rect.centery
            pygame.draw.line(surf, (220, 245, 255), (rect.x + 2, cy), (rect.right - 2, cy), 1)
        else:
            cx = rect.centerx
            pygame.draw.line(surf, (220, 245, 255), (cx, rect.y + 2), (cx, rect.bottom - 2), 1)

    def draw_preview(self, surf: pygame.Surface, wp: tuple[int, int] | None, horizontal: bool, is_valid: bool):
        if wp is None:
            return
        r, c = wp
        rect = self.wall_h_rect(r, c) if horizontal else self.wall_v_rect(r, c)
        color = C.C_WALL_PREV_OK if is_valid else C.C_WALL_PREV_BAD

        s = pygame.Surface(rect.size, pygame.SRCALPHA)
        s.fill(color)
        surf.blit(s, rect.topleft)
        pygame.draw.rect(surf, color[:3], rect, 2, border_radius=3)


class PawnView:
    def draw_pawns(self, surf: pygame.Surface, pawns: list[tuple[int, int]], tick: float):
        for player, (row, col) in enumerate(pawns):
            rect = BoardView.cell_rect(row, col)
            cx, cy = rect.centerx, rect.centery
            is_p1 = player == 0
            mc = C.C_P1 if is_p1 else C.C_P2
            dc = C.C_P1_DARK if is_p1 else C.C_P2_DARK
            lc = C.C_P1_LIGHT if is_p1 else C.C_P2_LIGHT
            gc = C.C_P1_GLOW if is_p1 else C.C_P2_GLOW

            pulse = 0.5 + 0.5 * math.sin(tick * 3 + player * math.pi)
            R = C.CELL // 2 - 4

            for i in range(11, 0, -1):
                alpha = int(gc[3] * (i / 11) * (0.7 + 0.3 * pulse))
                try:
                    pygame.gfxdraw.filled_circle(surf, cx, cy + 2, R + i, (*gc[:3], alpha))
                except Exception:
                    pass

            try:
                pygame.gfxdraw.filled_circle(surf, cx + 2, cy + 4, R, (0, 0, 0, 85))
            except Exception:
                pass

            for i in range(R, 0, -1):
                t = i / R
                rc = tuple(int(dc[j] * t + mc[j] * (1 - t)) for j in range(3))
                try:
                    pygame.gfxdraw.filled_circle(surf, cx, cy, i, rc)
                except Exception:
                    pass

            pygame.gfxdraw.aacircle(surf, cx, cy, R, mc)
            pygame.gfxdraw.filled_circle(surf, cx, cy, R, mc)

            base_rect = pygame.Rect(cx - R + 4, cy + R // 2, (R - 4) * 2, 4)
            pygame.draw.rect(surf, dc, base_rect, border_radius=2)
            pygame.draw.rect(surf, lc, base_rect, 1, border_radius=2)

            ring_color = (190, 225, 255) if is_p1 else (255, 200, 110)
            pygame.gfxdraw.aacircle(surf, cx, cy, R, ring_color)
            pygame.gfxdraw.aacircle(surf, cx, cy, R - 1, ring_color)

            bx, by_, br = cx - R // 3, cy - R // 3, max(1, R // 4)
            try:
                pygame.gfxdraw.filled_circle(surf, bx, by_, br, (*lc, 170))
                pygame.gfxdraw.aacircle(surf, bx, by_, br, (*lc, 170))
            except Exception:
                pass
