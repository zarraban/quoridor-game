from __future__ import annotations
import math
import pygame
from quoridor import constants as C


class MenuView:
    def __init__(self):
        pygame.font.init()
        self.font_title = pygame.font.SysFont("trebuchetms", 36, bold=True)
        self.font_subtitle = pygame.font.SysFont("trebuchetms", 18)
        self.font_btn = pygame.font.SysFont("trebuchetms", 22, bold=True)
        self.font_label = pygame.font.SysFont("trebuchetms", 16, bold=True)

        self.btn_pvp = pygame.Rect(0, 0, 1, 1)
        self.btn_bot = pygame.Rect(0, 0, 1, 1)
        self.btn_w1 = pygame.Rect(0, 0, 1, 1)
        self.btn_w3 = pygame.Rect(0, 0, 1, 1)
        self.btn_w5 = pygame.Rect(0, 0, 1, 1)
        self.btn_start = pygame.Rect(0, 0, 1, 1)

    def draw(self, surf: pygame.Surface, game_mode: str, target_wins: int, tick: float):
        overlay = pygame.Surface((C.WINDOW_W, C.WINDOW_H), pygame.SRCALPHA)
        overlay.fill((10, 14, 30, 180))
        surf.blit(overlay, (0, 0))

        center_x = C.WINDOW_W // 2

        pulse = 0.5 + 0.5 * math.sin(tick * 2)
        cr = int(190 + 35 * pulse)
        cg = int(205 + 35 * pulse)
        title_t = self.font_title.render("QUORIDOR  —  TACTICAL DUEL", True, (cr, cg, 255))
        surf.blit(title_t, title_t.get_rect(center=(center_x, 200)))

        sub_t = self.font_subtitle.render("Оберіть налаштування матчу", True, C.C_TEXT_DIM)
        surf.blit(sub_t, sub_t.get_rect(center=(center_x, 240)))

        mode_lbl = self.font_label.render("РЕЖИМ ГРИ", True, C.C_ACCENT)
        surf.blit(mode_lbl, mode_lbl.get_rect(center=(center_x, 320)))

        self.btn_pvp = pygame.Rect(center_x - 160, 350, 150, 50)
        self.btn_bot = pygame.Rect(center_x + 10, 350, 150, 50)
        self._draw_toggle_btn(surf, self.btn_pvp, "1 VS 1", game_mode == C.GAME_MODE_PVP)
        self._draw_toggle_btn(surf, self.btn_bot, "VS BOT", game_mode == C.GAME_MODE_BOT)

        wins_lbl = self.font_label.render("ГРАТИ ДО ПЕРЕМОГ", True, C.C_ACCENT)
        surf.blit(wins_lbl, wins_lbl.get_rect(center=(center_x, 440)))

        self.btn_w1 = pygame.Rect(center_x - 170, 470, 100, 50)
        self.btn_w3 = pygame.Rect(center_x - 50, 470, 100, 50)
        self.btn_w5 = pygame.Rect(center_x + 70, 470, 100, 50)

        self._draw_toggle_btn(surf, self.btn_w1, "1", target_wins == 1)
        self._draw_toggle_btn(surf, self.btn_w3, "3", target_wins == 3)
        self._draw_toggle_btn(surf, self.btn_w5, "5", target_wins == 5)

        self.btn_start = pygame.Rect(center_x - 120, 600, 240, 60)
        self._draw_action_btn(surf, self.btn_start, "ПОЧАТИ ДУЕЛЬ", tick)

    def _draw_toggle_btn(self, surf: pygame.Surface, rect: pygame.Rect, text: str, is_active: bool):
        mx, my = pygame.mouse.get_pos()
        is_hover = rect.collidepoint(mx, my)

        bg = C.C_BTN_ACTIVE_BG if is_active else (22, 28, 50)
        if is_hover and not is_active:
            bg = (35, 45, 75)
        bd = C.C_BTN_ACTIVE_BD if is_active else (50, 70, 120)

        pygame.draw.rect(surf, bg, rect, border_radius=8)
        pygame.draw.rect(surf, bd, rect, 2 if is_active else 1, border_radius=8)

        tc = (255, 255, 255) if is_active else (150, 180, 220)
        lbl = self.font_btn.render(text, True, tc)
        surf.blit(lbl, lbl.get_rect(center=rect.center))

    def _draw_action_btn(self, surf: pygame.Surface, rect: pygame.Rect, text: str, tick: float):
        mx, my = pygame.mouse.get_pos()
        is_hover = rect.collidepoint(mx, my)

        pulse = 0.5 + 0.5 * math.sin(tick * 5)
        r = int(90 + 30 * pulse)
        g = int(170 + 40 * pulse)
        b = 255
        bd = (r, g, b)

        bg = (38, 74, 140) if is_hover else (28, 64, 130)

        pygame.draw.rect(surf, bg, rect, border_radius=10)
        pygame.draw.rect(surf, bd, rect, 2, border_radius=10)

        lbl = self.font_btn.render(text, True, (255, 255, 255))
        surf.blit(lbl, lbl.get_rect(center=rect.center))
