from __future__ import annotations
import pygame
from quoridor import constants as C
from quoridor.game_state import GameState
from quoridor.particles import ParticleSystem
from quoridor.board_view import BoardView
from quoridor.pieces import WallView, PawnView
from quoridor.hud import HUD


class Renderer:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self._tick = 0.0

        self.particles = ParticleSystem(C.WINDOW_W, C.WINDOW_H)
        self.board = BoardView()
        self.walls = WallView()
        self.pawns = PawnView()
        self.hud = HUD()

    @property
    def toggle_btn_rect(self) -> pygame.Rect:
        return self.hud.toggle_btn_rect

    def update(self, dt: float):
        self._tick += dt * 0.001
        self.particles.update(dt)

    def draw_frame(self, gs: GameState,
                   valid_moves: list[tuple[int, int]],
                   mode: str,
                   wall_preview: tuple[int, int] | None,
                   wall_horizontal: bool,
                   hovered_cell: tuple[int, int] | None,
                   path_p0: list,
                   path_p1: list,
                   status_msg: str = ""):

        self.particles.draw(self.screen)

        self.board.draw_base(self.screen)
        self.board.draw_goal_glow(self.screen, self._tick)
        self.board.draw_paths(self.screen, path_p0, path_p1)
        self.board.draw_valid_moves(self.screen, valid_moves, mode, self._tick)
        self.board.draw_hover(self.screen, hovered_cell, mode)
        self.board.draw_coordinates(self.screen)

        self.walls.draw_placed_walls(self.screen, gs.h_walls, gs.v_walls)
        if wall_preview:
            is_valid = gs.can_place_wall(wall_preview[0], wall_preview[1], wall_horizontal)
            self.walls.draw_preview(self.screen, wall_preview, wall_horizontal, is_valid)

        self.pawns.draw_pawns(self.screen, gs.pawns, self._tick)

        self.hud.draw_title(self.screen, self._tick)
        self.hud.draw_player_card(self.screen, gs, player=0, x=14, y=10, flip=False, tick=self._tick)
        self.hud.draw_player_card(self.screen, gs, player=1, x=C.WINDOW_W - 224, y=10, flip=True, tick=self._tick)
        self.hud.draw_bottom_bar(self.screen, gs, mode, wall_horizontal, status_msg)
