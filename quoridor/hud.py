from __future__ import annotations
import math
import pygame
import pygame.gfxdraw
from quoridor import constants as C
from quoridor.game_state import GameState


class HUD:
    def __init__(self):
        pygame.font.init()
        self.font_title   = pygame.font.SysFont("trebuchetms", 20, bold=True)
        self.font_big     = pygame.font.SysFont("trebuchetms", 18, bold=True)
        self.font_med     = pygame.font.SysFont("trebuchetms", 15, bold=True)
        self.font_small   = pygame.font.SysFont("trebuchetms", 13)
        self.font_btn     = pygame.font.SysFont("trebuchetms", 15, bold=True)
        self.font_btn_sub = pygame.font.SysFont("trebuchetms", 12)
        self.font_name    = pygame.font.SysFont("trebuchetms", 16, bold=True)
        self.font_walls_n = pygame.font.SysFont("trebuchetms", 26, bold=True)
        self.font_tab     = pygame.font.SysFont("trebuchetms", 12, bold=True)

        self.toggle_btn_rect = pygame.Rect(0, 0, 1, 1)
        self.pvp_btn_rect = pygame.Rect(0, 0, 1, 1)
        self.bot_btn_rect = pygame.Rect(0, 0, 1, 1)

    def _draw_move_arrow(self, surf: pygame.Surface, cx: int, cy: int, size: int, color: tuple):
        arm = size // 2
        head = size // 3
        thick = max(2, size // 7)

        pygame.draw.line(surf, color, (cx - arm, cy), (cx + arm, cy), thick)
        pygame.draw.line(surf, color, (cx, cy - arm), (cx, cy + arm), thick)

        pygame.draw.polygon(surf, color, [(cx, cy - arm - 2), (cx - head, cy - arm + head), (cx + head, cy - arm + head)])
        pygame.draw.polygon(surf, color, [(cx, cy + arm + 2), (cx - head, cy + arm - head), (cx + head, cy + arm - head)])
        pygame.draw.polygon(surf, color, [(cx - arm - 2, cy), (cx - arm + head, cy - head), (cx - arm + head, cy + head)])
        pygame.draw.polygon(surf, color, [(cx + arm + 2, cy), (cx + arm - head, cy - head), (cx + arm - head, cy + head)])
        pygame.draw.circle(surf, (255, 255, 255), (cx, cy), max(2, size // 8))

    def _draw_wall_icon(self, surf: pygame.Surface, cx: int, cy: int, width: int, height: int, color: tuple):
        wrect = pygame.Rect(cx - width // 2, cy - height // 2, width, height)
        pygame.draw.rect(surf, color, wrect, border_radius=3)
        pygame.draw.rect(surf, (255, 255, 255), wrect, 1, border_radius=3)
        pygame.draw.line(surf, (255, 255, 255), (wrect.left + 3, cy), (wrect.right - 3, cy), 1)

    def draw_title_and_modes(self, surf: pygame.Surface, game_mode: str, tick: float):
        tw, th = 420, 32
        tx = C.WINDOW_W // 2 - tw // 2
        ty = 10

        tsurf = pygame.Surface((tw, th), pygame.SRCALPHA)
        tsurf.fill((10, 14, 32, 190))
        pygame.draw.rect(tsurf, (55, 85, 155), tsurf.get_rect(), 1, border_radius=6)
        surf.blit(tsurf, (tx, ty))

        pulse = 0.5 + 0.5 * math.sin(tick * 2)
        cr = int(190 + 35 * pulse)
        cg = int(205 + 35 * pulse)
        title_t = self.font_title.render("QUORIDOR  —  TACTICAL DUEL", True, (cr, cg, 255))
        surf.blit(title_t, title_t.get_rect(center=(C.WINDOW_W // 2, ty + th // 2)))

        mx, my = pygame.mouse.get_pos()
        tab_w, tab_h = 110, 26
        tab_y = 48
        center_x = C.WINDOW_W // 2

        self.pvp_btn_rect = pygame.Rect(center_x - tab_w - 6, tab_y, tab_w, tab_h)
        self.bot_btn_rect = pygame.Rect(center_x + 6, tab_y, tab_w, tab_h)

        for rect, mode_name, label in (
            (self.pvp_btn_rect, C.GAME_MODE_PVP, "1 VS 1 [F1]"),
            (self.bot_btn_rect, C.GAME_MODE_BOT, "VS BOT [F1]"),
        ):
            is_active = game_mode == mode_name
            is_hover = rect.collidepoint(mx, my)

            bg = C.C_BTN_ACTIVE_BG if is_active else (22, 28, 50)
            if is_hover and not is_active:
                bg = (35, 45, 75)
            bd = C.C_BTN_ACTIVE_BD if is_active else (50, 70, 120)

            ts = pygame.Surface(rect.size, pygame.SRCALPHA)
            ts.fill((*bg, 220))
            surf.blit(ts, rect.topleft)
            pygame.draw.rect(surf, bd, rect, 2 if is_active else 1, border_radius=5)

            tc = (255, 255, 255) if is_active else (150, 180, 220)
            lbl = self.font_tab.render(label, True, tc)
            surf.blit(lbl, lbl.get_rect(center=rect.center))

    def draw_player_card(self, surf: pygame.Surface, gs: GameState, player: int,
                         game_mode: str, x: int, y: int, flip: bool, tick: float):
        pw, ph = 210, 64
        is_active = gs.current_player == player and gs.winner is None
        is_p1 = player == 0
        pc = C.C_P1 if is_p1 else C.C_P2
        dc = C.C_P1_DARK if is_p1 else C.C_P2_DARK

        panel = pygame.Surface((pw, ph), pygame.SRCALPHA)
        panel.fill((10, 14, 30, 210))
        surf.blit(panel, (x, y))

        border_w = 2 if is_active else 1
        pulse = 0.5 + 0.5 * math.sin(tick * 3)
        brt = tuple(min(255, int(v * (1.0 + 0.3 * pulse))) for v in pc) if is_active else pc
        pygame.draw.rect(surf, brt, (x, y, pw, ph), border_w, border_radius=6)

        av_size = 46
        av_x = x + 6 if not flip else x + pw - av_size - 6
        av_rect = pygame.Rect(av_x, y + 9, av_size, av_size)
        pygame.draw.rect(surf, dc, av_rect, border_radius=5)
        pygame.draw.rect(surf, pc, av_rect, 2, border_radius=5)

        acx, acy = av_rect.centerx, av_rect.centery
        pygame.gfxdraw.aacircle(surf, acx, acy, 13, pc)
        pygame.gfxdraw.filled_circle(surf, acx, acy, 13, pc)
        pygame.gfxdraw.aacircle(surf, acx, acy, 13, (255, 255, 255))
        lbl = self.font_big.render(str(player + 1), True, (255, 255, 255))
        surf.blit(lbl, lbl.get_rect(center=(acx, acy)))

        if is_p1:
            name = "ICE MAGE [P1]"
        else:
            name = "FROST NOVA [BOT]" if game_mode == C.GAME_MODE_BOT else "FROST NOVA [P2]"

        tx = x + av_size + 14 if not flip else x + 12
        name_t = self.font_name.render(name, True, pc)
        surf.blit(name_t, (tx, y + 8))

        walls_label = self.font_small.render("WALLS", True, (130, 155, 195))
        surf.blit(walls_label, (tx, y + 32))
        walls_n = self.font_walls_n.render(str(gs.walls_left[player]), True, pc)
        surf.blit(walls_n, (tx + 50, y + 23))

        if is_active:
            ind = pygame.Surface((pw, 3), pygame.SRCALPHA)
            ind.fill((*pc, 240))
            surf.blit(ind, (x, y + ph - 3))

    def draw_bottom_bar(self, surf: pygame.Surface, gs: GameState, mode: str,
                        game_mode: str, wall_horizontal: bool,
                        status_msg: str, is_bot_thinking: bool = False):
        bh = C.BOTTOM_BAR_H
        by = C.WINDOW_H - bh

        bar = pygame.Surface((C.WINDOW_W, bh), pygame.SRCALPHA)
        bar.fill((8, 11, 26, 235))
        surf.blit(bar, (0, by))
        pygame.draw.line(surf, (50, 75, 140), (0, by), (C.WINDOW_W, by), 2)

        center_x = C.WINDOW_W // 2
        btn_w, btn_h = 260, 56
        btn_x = center_x - btn_w // 2
        btn_y = by + 16
        self.toggle_btn_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)

        mx, my = pygame.mouse.get_pos()
        hovered = self.toggle_btn_rect.collidepoint(mx, my)

        is_move = mode == C.MODE_MOVE
        bg_col = C.C_BTN_ACTIVE_BG if is_move else (35, 45, 80)
        if hovered:
            bg_col = tuple(min(255, v + 25) for v in bg_col)
        bd_col = C.C_BTN_ACTIVE_BD if is_move else C.C_WALL_BLUE

        bsurf = pygame.Surface(self.toggle_btn_rect.size, pygame.SRCALPHA)
        bsurf.fill((*bg_col, 230))
        surf.blit(bsurf, self.toggle_btn_rect.topleft)
        pygame.draw.rect(surf, bd_col, self.toggle_btn_rect, 2, border_radius=8)

        icon_cx = btn_x + 36
        icon_cy = btn_y + btn_h // 2

        if is_move:
            self._draw_move_arrow(surf, icon_cx, icon_cy, size=24, color=(140, 220, 255))
            title_txt = "РЕЖИМ: ХІД [M / Space]"
            sub_txt   = "Натисни, щоб обрати стінку"
        else:
            self._draw_wall_icon(surf, icon_cx, icon_cy, width=28, height=12, color=C.C_WALL_BLUE)
            title_txt = "РЕЖИМ: СТІНКА [W / Space]"
            sub_txt   = "[R] Повернути (гориз / вертик)"

        main_t = self.font_btn.render(title_txt, True, C.C_BTN_TEXT)
        sub_t  = self.font_btn_sub.render(sub_txt, True, C.C_BTN_SUBTEXT)
        surf.blit(main_t, (btn_x + 64, btn_y + 10))
        surf.blit(sub_t,  (btn_x + 64, btn_y + 32))

        if gs.winner is not None:
            wc = C.C_P1 if gs.winner == 0 else C.C_P2
            wn = "ICE MAGE" if gs.winner == 0 else ("FROST NOVA [BOT]" if game_mode == C.GAME_MODE_BOT else "FROST NOVA")
            wt = self.font_big.render(f"{wn} ПЕРЕМІГ! 🏆", True, wc)
            surf.blit(wt, (24, by + 30))
        elif is_bot_thinking:
            wt = self.font_big.render("БОТ ОБЧИСЛЮЄ ХІД...", True, C.C_ACCENT)
            surf.blit(wt, (24, by + 30))
        else:
            cp = gs.current_player
            pc = C.C_P1 if cp == 0 else C.C_P2
            if cp == 0:
                nm = "ХІД: ICE MAGE"
            else:
                nm = "ХІД: FROST NOVA [BOT]" if game_mode == C.GAME_MODE_BOT else "ХІД: FROST NOVA [P2]"
            turn_t = self.font_big.render(nm, True, pc)
            surf.blit(turn_t, (24, by + 30))

        if mode == C.MODE_WALL:
            orient_str = "Горизонтальна" if wall_horizontal else "Вертикальна"
            ot = self.font_med.render(f"Стінка: {orient_str}", True, C.C_ACCENT)
            surf.blit(ot, (C.WINDOW_W - 220, by + 22))
            r_hint = self.font_small.render("[R] повернути", True, C.C_TEXT_DIM)
            surf.blit(r_hint, (C.WINDOW_W - 220, by + 44))
        else:
            hints = ["[F1] Зміна режиму гри", "[F2] Нова гра", "[ПКМ/Esc] Скасувати"]
            for idx, h in enumerate(hints):
                ht = self.font_small.render(h, True, (120, 145, 190))
                surf.blit(ht, (C.WINDOW_W - 200, by + 16 + idx * 18))

        if status_msg:
            st = self.font_med.render(status_msg, True, C.C_ERROR)
            sbg = pygame.Surface((st.get_width() + 20, st.get_height() + 8), pygame.SRCALPHA)
            sbg.fill((60, 12, 12, 210))
            sx = center_x - sbg.get_width() // 2
            sy = by - sbg.get_height() - 6
            surf.blit(sbg, (sx, sy))
            pygame.draw.rect(surf, (190, 50, 50), (sx, sy, sbg.get_width(), sbg.get_height()), 1, border_radius=4)
            surf.blit(st, (sx + 10, sy + 4))
