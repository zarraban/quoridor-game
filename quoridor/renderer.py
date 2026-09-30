from __future__ import annotations
import math, random
import pygame
import pygame.gfxdraw
from quoridor import constants as C
from quoridor.game_state import GameState


def cell_rect(row: int, col: int) -> pygame.Rect:
    x = C.BOARD_OFFSET_X + col * C.STEP
    y = C.BOARD_OFFSET_Y + row * C.STEP
    return pygame.Rect(x, y, C.CELL, C.CELL)

def wall_h_rect(r: int, c: int) -> pygame.Rect:
    x = C.BOARD_OFFSET_X + c * C.STEP
    y = C.BOARD_OFFSET_Y + (r + 1) * C.STEP - C.GAP
    return pygame.Rect(x, y, 2 * C.CELL + C.GAP, C.GAP)

def wall_v_rect(r: int, c: int) -> pygame.Rect:
    x = C.BOARD_OFFSET_X + (c + 1) * C.STEP - C.GAP
    y = C.BOARD_OFFSET_Y + r * C.STEP
    return pygame.Rect(x, y, C.GAP, 2 * C.CELL + C.GAP)

def _aa_circle(surf, color, cx, cy, r):
    if r <= 0: return
    pygame.gfxdraw.aacircle(surf, cx, cy, r, color)
    pygame.gfxdraw.filled_circle(surf, cx, cy, r, color)

def _rrect(surf, color, rect, radius=4, width=0):
    pygame.draw.rect(surf, color, rect, width, border_radius=radius)

def _glow_rect(surf, color, rect, blur=8, radius=4):
    for i in range(blur, 0, -1):
        alpha = int(80 * (i / blur))
        expanded = rect.inflate(i * 2, i * 2)
        s = pygame.Surface(expanded.size, pygame.SRCALPHA)
        pygame.draw.rect(s, (*color[:3], alpha), s.get_rect(), border_radius=radius + i)
        surf.blit(s, expanded.topleft)

def _glow_circle(surf, color, cx, cy, r, blur=10):
    for i in range(blur, 0, -1):
        alpha = int(90 * (i / blur))
        try:
            pygame.gfxdraw.filled_circle(surf, cx, cy, r + i, (*color[:3], alpha))
        except Exception:
            pass


class Renderer:
    RUNE_CHARS = "ᚠᚢᚦᚨᚱᚲᚷᚹᚺᚾᛁᛃᛇᛈᛉᛊᛏᛒᛖᛗᛚᛜᛞᛟ"

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        pygame.font.init()
        self.font_title   = pygame.font.SysFont("segoeui",  22, bold=True)
        self.font_big     = pygame.font.SysFont("segoeui",  18, bold=True)
        self.font_med     = pygame.font.SysFont("segoeui",  15)
        self.font_small   = pygame.font.SysFont("segoeui",  12)
        self.font_btn     = pygame.font.SysFont("segoeui",  13, bold=True)
        self.font_rune    = pygame.font.SysFont("segoeui",  11)
        self.font_name    = pygame.font.SysFont("segoeui",  16, bold=True)
        self.font_walls_n = pygame.font.SysFont("segoeui",  26, bold=True)

        self._tick = 0
        self._particles: list[dict] = []
        self._init_particles()

        self._bg_surf     = self._build_bg()
        self._board_surf  = self._build_board()

    def _init_particles(self):
        for _ in range(40):
            self._particles.append(self._new_particle(random.randint(0, C.WINDOW_H)))

    def _new_particle(self, y=None):
        return {
            "x": random.uniform(0, C.WINDOW_W),
            "y": y if y is not None else C.WINDOW_H,
            "vy": random.uniform(0.2, 0.8),
            "r": random.uniform(1, 3),
            "alpha": random.randint(40, 140),
            "color": random.choice([(80, 140, 255), (120, 200, 255), (200, 160, 255)]),
        }

    def _build_bg(self) -> pygame.Surface:
        s = pygame.Surface((C.WINDOW_W, C.WINDOW_H))
        for y in range(C.WINDOW_H):
            t = y / C.WINDOW_H
            r = int(C.C_BG_TOP[0] * (1 - t) + C.C_BG_BOT[0] * t)
            g = int(C.C_BG_TOP[1] * (1 - t) + C.C_BG_BOT[1] * t)
            b = int(C.C_BG_TOP[2] * (1 - t) + C.C_BG_BOT[2] * t)
            pygame.draw.line(s, (r, g, b), (0, y), (C.WINDOW_W, y))

        # Гори (силуети)
        mountain_color = (14, 18, 38)
        for mx, mh, mw in [(100, 320, 180), (280, 260, 140), (820, 340, 200),
                            (960, 280, 160), (50, 200, 120), (700, 300, 170),
                            (500, 180, 130)]:
            pts = [(mx - mw, C.WINDOW_H), (mx, C.WINDOW_H - mh),
                   (mx + mw, C.WINDOW_H)]
            pygame.draw.polygon(s, mountain_color, pts)

        # Небесне сяйво (aurora)
        for i in range(3):
            ax = 200 + i * 300
            aurora = pygame.Surface((300, 400), pygame.SRCALPHA)
            for y in range(400):
                alpha = int(15 * math.sin(y / 40) * (1 - y / 400))
                if alpha > 0:
                    col = [(60, 120, 255), (80, 200, 160), (160, 80, 255)][i]
                    pygame.draw.line(aurora, (*col, alpha), (0, y), (300, y))
            s.blit(aurora, (ax, 0))

        return s

    def _build_board(self) -> pygame.Surface:
        pad = 12
        w = C.BOARD_PX + pad * 2
        h = C.BOARD_PX + pad * 2
        s = pygame.Surface((w, h), pygame.SRCALPHA)

        # Зовнішня рамка (камінь)
        outer = pygame.Rect(0, 0, w, h)
        _rrect(s, (20, 24, 38), outer, radius=8)
        _rrect(s, (45, 55, 80), outer, radius=8, width=2)

        # Внутрішній фон
        inner = pygame.Rect(pad - 4, pad - 4, C.BOARD_PX + 8, C.BOARD_PX + 8)
        _rrect(s, (18, 22, 34), inner, radius=6)

        rng = random.Random(42)

        for r in range(C.BOARD_SIZE):
            for c in range(C.BOARD_SIZE):
                x = pad + c * C.STEP
                y = pad + r * C.STEP
                rect = pygame.Rect(x, y, C.CELL, C.CELL)

                # Основа клітинки
                shade = rng.randint(-4, 4)
                base = tuple(max(0, min(255, v + shade)) for v in C.C_STONE_MID)
                _rrect(s, base, rect, radius=3)

                # Кам'яна текстура (тріщини / лінії)
                for _ in range(2):
                    lx1 = x + rng.randint(4, C.CELL - 8)
                    ly1 = y + rng.randint(4, C.CELL - 8)
                    lx2 = lx1 + rng.randint(-8, 8)
                    ly2 = ly1 + rng.randint(-8, 8)
                    pygame.draw.line(s, C.C_STONE_LINE, (lx1, ly1), (lx2, ly2), 1)

                # Руна (рідко)
                if rng.random() < 0.25:
                    ch = rng.choice(self.RUNE_CHARS)
                    rt = self.font_rune.render(ch, True, (*C.C_RUNE[:3], 70))
                    s.blit(rt, rt.get_rect(center=(x + C.CELL // 2, y + C.CELL // 2)))

                # Рамка клітинки
                _rrect(s, C.C_STONE_LINE, rect, radius=3, width=1)

        self._board_pad = pad
        return s

    def update(self, dt: float):
        self._tick += dt * 0.001
        for p in self._particles:
            p["y"] -= p["vy"]
            if p["y"] < 0:
                self._particles[self._particles.index(p)] = self._new_particle()

    def draw_frame(self, gs: GameState,
                   valid_moves, mode, wall_preview,
                   wall_horizontal, hovered_cell,
                   path_p0, path_p1, status_msg=""):

        # Фон
        self.screen.blit(self._bg_surf, (0, 0))
        self._draw_particles()

        # Дошка
        bx = C.BOARD_OFFSET_X - self._board_pad
        by = C.BOARD_OFFSET_Y - self._board_pad
        self.screen.blit(self._board_surf, (bx, by))

        # Шари поверх дошки
        self._draw_goal_glow(gs)
        self._draw_paths(path_p0, path_p1)
        self._draw_valid_moves(valid_moves, mode)
        self._draw_hover(hovered_cell, mode)
        self._draw_placed_walls(gs)
        self._draw_wall_preview(wall_preview, wall_horizontal, gs)
        self._draw_pawns(gs)

        # HUD
        self._draw_title()
        self._draw_player_panel_left(gs)
        self._draw_player_panel_right(gs)
        self._draw_bottom_bar(gs, mode, wall_horizontal, status_msg)

    def _draw_particles(self):
        for p in self._particles:
            try:
                pygame.gfxdraw.filled_circle(
                    self.screen, int(p["x"]), int(p["y"]),
                    int(p["r"]), (*p["color"], p["alpha"]))
            except Exception:
                pass

    def _draw_goal_glow(self, gs: GameState):
        pulse = 0.5 + 0.5 * math.sin(self._tick * 3)

        for row, glow_c, line_c in (
            (0,               C.C_GOAL_P1_GLOW, C.C_GOAL_P1_LINE),
            (C.BOARD_SIZE - 1, C.C_GOAL_P2_GLOW, C.C_GOAL_P2_LINE),
        ):
            x = C.BOARD_OFFSET_X
            y = C.BOARD_OFFSET_Y + row * C.STEP

            # Сяйво клітинок
            for c in range(C.BOARD_SIZE):
                rect = cell_rect(row, c)
                s = pygame.Surface((C.CELL, C.CELL), pygame.SRCALPHA)
                alpha = int(glow_c[3] * (0.7 + 0.3 * pulse))
                s.fill((*glow_c[:3], alpha))
                self.screen.blit(s, rect.topleft)

            # Лінія-межа
            lw = C.BOARD_PX
            line_y = y + (0 if row == 0 else C.CELL)
            for thickness, alpha in ((6, 40), (3, 100), (1, 200)):
                ls = pygame.Surface((lw, thickness), pygame.SRCALPHA)
                ls.fill((*line_c[:3], int(alpha * (0.8 + 0.2 * pulse))))
                self.screen.blit(ls, (x, line_y - thickness // 2))

    def _draw_paths(self, p0, p1):
        for path, color in ((p0, C.C_P1), (p1, C.C_P2)):
            for i, (r, c) in enumerate(path[1:-1], 1):
                rect = cell_rect(r, c)
                s = pygame.Surface((C.CELL, C.CELL), pygame.SRCALPHA)
                alpha = max(10, 30 - i * 3)
                s.fill((*color, alpha))
                self.screen.blit(s, rect.topleft)

    def _draw_valid_moves(self, moves, mode):
        if mode != C.MODE_MOVE:
            return
        pulse = 0.5 + 0.5 * math.sin(self._tick * 4)
        for r, c in moves:
            rect = cell_rect(r, c)
            s = pygame.Surface((C.CELL, C.CELL), pygame.SRCALPHA)
            s.fill((*C.C_CELL_VALID[:3], int(C.C_CELL_VALID[3] * (0.7 + 0.3 * pulse))))
            self.screen.blit(s, rect.topleft)
            _rrect(self.screen, (*C.C_CELL_VALID_DOT, 200), rect, radius=3, width=2)
            cx, cy = rect.centerx, rect.centery
            dot_r = int(6 + 2 * pulse)
            _aa_circle(self.screen, (*C.C_CELL_VALID_DOT, 180), cx, cy, dot_r)
            _aa_circle(self.screen, (255, 255, 255, 220), cx, cy, dot_r - 3)

    def _draw_hover(self, cell, mode):
        if cell is None or mode != C.MODE_MOVE:
            return
        r, c = cell
        rect = cell_rect(r, c)
        s = pygame.Surface((C.CELL, C.CELL), pygame.SRCALPHA)
        s.fill((*C.C_CELL_HOVER[:3], C.C_CELL_HOVER[3]))
        self.screen.blit(s, rect.topleft)
        _rrect(self.screen, (120, 180, 255, 150), rect, radius=3, width=2)

    def _draw_placed_walls(self, gs: GameState):
        for r, c in gs.h_walls:
            self._draw_fancy_wall(wall_h_rect(r, c), horizontal=True, player_wall=True)
        for r, c in gs.v_walls:
            self._draw_fancy_wall(wall_v_rect(r, c), horizontal=False, player_wall=True)

    def _draw_fancy_wall(self, rect: pygame.Rect, horizontal: bool, player_wall=True):
        glow_color = C.C_WALL_BLUE
        glow_surf_color = C.C_WALL_GLOW_B

        # Зовнішнє сяйво (багатошарове)
        for i in range(10, 0, -1):
            exp = rect.inflate(i * 2, i * 2)
            gs = pygame.Surface(exp.size, pygame.SRCALPHA)
            alpha = int(50 * (i / 10))
            pygame.draw.rect(gs, (*glow_color, alpha), gs.get_rect(), border_radius=3 + i)
            self.screen.blit(gs, exp.topleft)

        # Основа стінки (напівпрозора)
        wall_surf = pygame.Surface(rect.size, pygame.SRCALPHA)
        wall_surf.fill((*glow_color, 80))
        self.screen.blit(wall_surf, rect.topleft)

        # Зовнішня рамка (яскрава)
        _rrect(self.screen, glow_color, rect, radius=3, width=2)

        # Центральна лінія (найяскравіший момент)
        if horizontal:
            cy = rect.centery
            pygame.draw.line(self.screen, (200, 235, 255), (rect.x + 2, cy), (rect.right - 2, cy), 1)
        else:
            cx = rect.centerx
            pygame.draw.line(self.screen, (200, 235, 255), (cx, rect.y + 2), (cx, rect.bottom - 2), 1)

    def _draw_wall_preview(self, wp, horizontal, gs: GameState):
        if wp is None:
            return
        r, c = wp
        valid = gs.can_place_wall(r, c, horizontal)
        rect = wall_h_rect(r, c) if horizontal else wall_v_rect(r, c)
        color = C.C_WALL_PREV_OK if valid else C.C_WALL_PREV_BAD

        s = pygame.Surface(rect.size, pygame.SRCALPHA)
        s.fill(color)
        self.screen.blit(s, rect.topleft)
        _rrect(self.screen, color[:3], rect, radius=3, width=2)

    def _draw_pawns(self, gs: GameState):
        for player, (row, col) in enumerate(gs.pawns):
            rect = cell_rect(row, col)
            cx, cy = rect.centerx, rect.centery
            is_p1  = player == 0
            mc     = C.C_P1      if is_p1 else C.C_P2
            dc     = C.C_P1_DARK if is_p1 else C.C_P2_DARK
            lc     = C.C_P1_LIGHT if is_p1 else C.C_P2_LIGHT
            gc     = C.C_P1_GLOW  if is_p1 else C.C_P2_GLOW

            pulse = 0.5 + 0.5 * math.sin(self._tick * 3 + player * math.pi)
            R = C.CELL // 2 - 4

            # Зовнішнє сяйво
            for i in range(12, 0, -1):
                alpha = int(gc[3] * (i / 12) * (0.7 + 0.3 * pulse))
                try:
                    pygame.gfxdraw.filled_circle(
                        self.screen, cx, cy + 2, R + i, (*gc[:3], alpha))
                except Exception:
                    pass

            # Тінь
            try:
                pygame.gfxdraw.filled_circle(self.screen, cx + 2, cy + 4, R, (0, 0, 0, 80))
            except Exception:
                pass

            # Тіло фігури (градієнт)
            for i in range(R, 0, -1):
                t = i / R
                rc = tuple(int(dc[j] * t + mc[j] * (1 - t)) for j in range(3))
                try:
                    pygame.gfxdraw.filled_circle(self.screen, cx, cy, i, rc)
                except Exception:
                    pass

            _aa_circle(self.screen, mc, cx, cy, R)

            # Шахматна фігура: основа (низ)
            base_rect = pygame.Rect(cx - R + 4, cy + R // 2, (R - 4) * 2, 5)
            _rrect(self.screen, dc, base_rect, radius=2)
            _rrect(self.screen, lc, base_rect, radius=2, width=1)

            # Зовнішнє кільце (золото/біле)
            ring_color = (220, 190, 80) if not is_p1 else (180, 220, 255)
            _aa_circle(self.screen, ring_color, cx, cy, R)
            pygame.gfxdraw.aacircle(self.screen, cx, cy, R - 1, ring_color)

            # Блик
            bx, by_, br = cx - R // 3, cy - R // 3, max(1, R // 4)
            try:
                pygame.gfxdraw.filled_circle(self.screen, bx, by_, br, (*lc, 160))
                pygame.gfxdraw.aacircle(self.screen, bx, by_, br, (*lc, 160))
            except Exception:
                pass

    # ── Title bar ────────────────────────────────────────────────
    def _draw_title(self):
        title_surf = pygame.Surface((500, 44), pygame.SRCALPHA)
        title_surf.fill((8, 12, 30, 180))
        pygame.draw.rect(title_surf, (50, 80, 150), title_surf.get_rect(), 1, border_radius=6)
        tx = C.WINDOW_W // 2 - 250
        ty = 14
        self.screen.blit(title_surf, (tx, ty))

        pulse = 0.5 + 0.5 * math.sin(self._tick * 2)
        cr = int(180 + 40 * pulse)
        cg = int(190 + 40 * pulse)
        title_t = self.font_title.render("QUORIDOR  —  TACTICAL DUEL", True, (cr, cg, 255))
        self.screen.blit(title_t, title_t.get_rect(center=(C.WINDOW_W // 2, ty + 22)))

    # ── Панель гравця (ліво) ─────────────────────────────────────
    def _draw_player_panel_left(self, gs: GameState):
        self._draw_player_panel(gs, player=0, x=8, y=8, flip=False)

    def _draw_player_panel_right(self, gs: GameState):
        self._draw_player_panel(gs, player=1, x=C.WINDOW_W - 218, y=8, flip=True)

    def _draw_player_panel(self, gs: GameState, player: int,
                            x: int, y: int, flip: bool):
        pw, ph = 210, 68
        is_active = gs.current_player == player and gs.winner is None
        is_p1 = player == 0
        pc = C.C_P1 if is_p1 else C.C_P2
        dc = C.C_P1_DARK if is_p1 else C.C_P2_DARK
        border_c = C.C_PANEL_P1 if is_p1 else C.C_PANEL_P2

        # Фон панелі
        panel = pygame.Surface((pw, ph), pygame.SRCALPHA)
        panel.fill((8, 12, 28, 200))
        self.screen.blit(panel, (x, y))

        # Рамка (активна — яскравіша)
        border_alpha = 255 if is_active else 130
        border_w = 2 if is_active else 1
        pulse = 0.5 + 0.5 * math.sin(self._tick * 3)
        brt = tuple(min(255, int(v * (1.0 + 0.3 * pulse))) for v in pc) if is_active else pc
        pygame.draw.rect(self.screen, (*brt, border_alpha),
                         (x, y, pw, ph), border_w, border_radius=6)

        # Аватар (кольоровий квадрат з фігурою)
        av_size = 50
        av_x = x + 4 if not flip else x + pw - av_size - 4
        av_rect = pygame.Rect(av_x, y + 8, av_size, av_size)
        pygame.draw.rect(self.screen, dc, av_rect, border_radius=5)
        pygame.draw.rect(self.screen, pc, av_rect, 2, border_radius=5)

        # Міні-фігура в аватарці
        acx, acy = av_rect.centerx, av_rect.centery
        _aa_circle(self.screen, pc, acx, acy, 14)
        _aa_circle(self.screen, (255, 255, 255), acx, acy, 14)
        pygame.gfxdraw.aacircle(self.screen, acx, acy, 13, (255, 255, 255))
        lbl = self.font_btn.render(str(player + 1), True, (255, 255, 255))
        self.screen.blit(lbl, lbl.get_rect(center=(acx, acy)))

        # Ім'я
        name = "ICE MAGE" if is_p1 else "FROST NOVA"
        tx = x + av_size + 10 if not flip else x + 8
        name_t = self.font_name.render(name, True, pc)
        self.screen.blit(name_t, (tx, y + 10))

        # Стінки
        walls_label = self.font_small.render("WALLS", True, (100, 120, 160))
        self.screen.blit(walls_label, (tx, y + 30))
        walls_n = self.font_walls_n.render(str(gs.walls_left[player]), True, pc)
        self.screen.blit(walls_n, (tx + 46, y + 22))

        # Активний індикатор
        if is_active:
            ind = pygame.Surface((pw, 3), pygame.SRCALPHA)
            ind.fill((*pc, 220))
            self.screen.blit(ind, (x, y + ph - 3))

    # ── Нижня панель ─────────────────────────────────────────────
    def _draw_bottom_bar(self, gs: GameState, mode: str,
                          wall_horizontal: bool, status_msg: str):
        bh = C.BOTTOM_BAR_H
        by = C.WINDOW_H - bh

        # Фон
        bar = pygame.Surface((C.WINDOW_W, bh), pygame.SRCALPHA)
        bar.fill((6, 8, 22, 220))
        self.screen.blit(bar, (0, by))
        pygame.draw.line(self.screen, (50, 70, 130),
                         (0, by), (C.WINDOW_W, by), 2)

        center_x = C.WINDOW_W // 2
        btn_y = by + 15
        btn_h = 52
        btn_w = 110

        # Ім'я активного гравця
        if gs.winner is None:
            cp = gs.current_player
            pc = C.C_P1 if cp == 0 else C.C_P2
            nm = "ICE MAGE" if cp == 0 else "FROST NOVA"
            label_t = self.font_big.render(nm, True, pc)
            self.screen.blit(label_t, label_t.get_rect(
                center=(center_x, by + 12)))
        else:
            wc = C.C_P1 if gs.winner == 0 else C.C_P2
            wn = "ICE MAGE" if gs.winner == 0 else "FROST NOVA"
            wt = self.font_big.render(f"🏆  {wn}  WINS!", True, wc)
            self.screen.blit(wt, wt.get_rect(center=(center_x, by + 12)))

        # Кнопки
        btns = [
            (C.MODE_MOVE, "♟", "Move"),
            (C.MODE_WALL, "▬", "Walls"),
        ]
        total_w = len(btns) * (btn_w + 10) - 10
        bx_start = center_x - total_w // 2

        for i, (bmode, icon, label) in enumerate(btns):
            bx = bx_start + i * (btn_w + 10)
            is_active = mode == bmode
            brect = pygame.Rect(bx, btn_y, btn_w, btn_h)

            # Фон кнопки
            bg_color = C.C_BTN_ACTIVE_BG if is_active else C.C_BTN_BG
            bd_color = C.C_BTN_ACTIVE_BD if is_active else C.C_BTN_BORDER

            btn_surf = pygame.Surface(brect.size, pygame.SRCALPHA)
            btn_surf.fill((*bg_color, 220))
            self.screen.blit(btn_surf, brect.topleft)
            pygame.draw.rect(self.screen, bd_color, brect, 2, border_radius=6)

            # Сяйво активної кнопки
            if is_active:
                _glow_rect(self.screen, C.C_BTN_ACTIVE_BD, brect, blur=6)

            # Іконка + текст
            tc = C.C_BTN_ACTIVE_T if is_active else C.C_BTN_TEXT
            icon_t = self.font_big.render(icon, True, tc)
            label_t = self.font_btn.render(label, True, tc)
            self.screen.blit(icon_t, icon_t.get_rect(center=(brect.centerx, brect.centery - 8)))
            self.screen.blit(label_t, label_t.get_rect(center=(brect.centerx, brect.centery + 14)))

        # Орієнтація стінки
        if mode == C.MODE_WALL:
            orient = ("━ Horizontal" if wall_horizontal else "┃ Vertical") + "  [R]"
            ot = self.font_small.render(orient, True, C.C_ACCENT)
            self.screen.blit(ot, ot.get_rect(
                center=(bx_start + total_w + 70, by + bh // 2)))

        # Підказки (зліва)
        hints = [("F2", "new game"), ("Esc", "cancel"), ("M/W", "mode")]
        hx = 20
        for key, desc in hints:
            kt = self.font_small.render(f"[{key}]", True, (80, 110, 180))
            dt = self.font_small.render(desc, True, C.C_TEXT_DIM)
            self.screen.blit(kt, (hx, by + 20))
            self.screen.blit(dt, (hx, by + 34))
            hx += 80

        # Статус/помилка
        if status_msg:
            st = self.font_med.render(status_msg, True, C.C_ERROR)
            sbg = pygame.Surface((st.get_width() + 16, st.get_height() + 8), pygame.SRCALPHA)
            sbg.fill((60, 10, 10, 180))
            sx = center_x - sbg.get_width() // 2
            self.screen.blit(sbg, (sx, by + bh - st.get_height() - 12))
            self.screen.blit(st, (sx + 8, by + bh - st.get_height() - 8))

        # Координати (зовні панелі — зверху від неї)
        self._draw_coordinates()

    def _draw_coordinates(self):
        cols = "ABCDEFGHI"
        for i in range(C.BOARD_SIZE):
            lx = C.BOARD_OFFSET_X + i * C.STEP + C.CELL // 2
            ly = C.BOARD_OFFSET_Y - 16
            t = self.font_small.render(cols[i], True, (70, 95, 140))
            self.screen.blit(t, t.get_rect(center=(lx, ly)))

            nx = C.BOARD_OFFSET_X - 14
            ny = C.BOARD_OFFSET_Y + i * C.STEP + C.CELL // 2
            n = self.font_small.render(str(9 - i), True, (70, 95, 140))
            self.screen.blit(n, n.get_rect(center=(nx, ny)))
