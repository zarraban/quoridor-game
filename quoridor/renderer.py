from __future__ import annotations
import pygame
from quoridor import constants as C
from quoridor.game_state import GameState
from quoridor.board_view import BoardView
from quoridor.pieces import WallView, PawnView
from quoridor.hud import HUD
from quoridor.particles import ParticleSystem
from quoridor.menu_view import MenuView


class Renderer:
    def __init__(self, window: pygame.Surface):
        self.window = window
        self.board_view = BoardView()
        self.wall_view = WallView()
        self.pawn_view = PawnView()
        self.hud = HUD()
        self.menu_view = MenuView()
        self.particles = ParticleSystem(C.WINDOW_W, C.WINDOW_H)
        self.tick = 0.0

        bg_top = C.C_BG_TOP
        bg_mid = C.C_BG_MID
        bg_bot = C.C_BG_BOT

        self.bg_surf = pygame.Surface((C.WINDOW_W, C.WINDOW_H))
        for y in range(C.WINDOW_H):
            if y < C.WINDOW_H // 2:
                ratio = y / (C.WINDOW_H / 2)
                r = int(bg_top[0] + (bg_mid[0] - bg_top[0]) * ratio)
                g = int(bg_top[1] + (bg_mid[1] - bg_top[1]) * ratio)
                b = int(bg_top[2] + (bg_mid[2] - bg_top[2]) * ratio)
            else:
                ratio = (y - C.WINDOW_H / 2) / (C.WINDOW_H / 2)
                r = int(bg_mid[0] + (bg_bot[0] - bg_mid[0]) * ratio)
                g = int(bg_mid[1] + (bg_bot[1] - bg_mid[1]) * ratio)
                b = int(bg_mid[2] + (bg_bot[2] - bg_mid[2]) * ratio)
            pygame.draw.line(self.bg_surf, (r, g, b), (0, y), (C.WINDOW_W, y))

    def update(self, dt: float):
        self.tick += dt
        self.particles.update(dt)

    def draw(self, app_state: str, gs: GameState, mode: str, game_mode: str,
             target_wins: int, scores: list[int],
             wall_horiz: bool, hover_cell: tuple[int, int] | None,
             status_msg: str, bot_thinking: bool):
        self.window.blit(self.bg_surf, (0, 0))

        self.particles.draw(self.window)

        if app_state == C.STATE_MENU:
            self.menu_view.draw(self.window, game_mode, target_wins, self.tick)
            return

        self.board_view.draw_base(self.window)
        self.board_view.draw_coordinates(self.window)
        self.board_view.draw_goal_glow(self.window, self.tick)
        if gs.winner is None and not bot_thinking:
            valid_moves = gs.get_valid_moves()
            self.board_view.draw_valid_moves(self.window, valid_moves, mode, self.tick)
        self.board_view.draw_hover(self.window, hover_cell, mode)
        
        self.wall_view.draw_placed_walls(self.window, gs.h_walls, gs.v_walls)
        self.pawn_view.draw_pawns(self.window, gs.pawns, self.tick)
        self.hud.draw_title(self.window, self.tick)
        self.hud.draw_player_card(self.window, gs, 0, game_mode, scores[0], target_wins, 24, 24, False, self.tick)
        self.hud.draw_player_card(self.window, gs, 1, game_mode, scores[1], target_wins, C.WINDOW_W - 264, 24, True, self.tick)
        self.hud.draw_bottom_bar(self.window, gs, mode, game_mode, wall_horiz, status_msg, bot_thinking)

        if gs.winner is None and not bot_thinking:
            if mode == C.MODE_WALL and hover_cell:
                r, c = hover_cell
                if 0 <= r < C.BOARD_SIZE - 1 and 0 <= c < C.BOARD_SIZE - 1:
                    is_valid = gs.can_place_wall(r, c, wall_horiz)
                    self.wall_view.draw_preview(self.window, (r, c), wall_horiz, is_valid)
