from __future__ import annotations
import sys
import pygame
from quoridor import constants as C
from quoridor.game_state import GameState
from quoridor.board_view import BoardView
from quoridor.pieces import WallView
from quoridor.renderer import Renderer


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Quoridor — Tactical Duel")

        icon = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.circle(icon, C.C_P1, (16, 16), 14)
        pygame.draw.circle(icon, (255, 255, 255), (16, 16), 14, 2)
        pygame.display.set_icon(icon)

        self.screen = pygame.display.set_mode((C.WINDOW_W, C.WINDOW_H))
        self.clock = pygame.time.Clock()
        self.renderer = Renderer(self.screen)

        self.state = GameState()
        self.mode = C.MODE_MOVE
        self.wall_horizontal = True
        self.wall_preview: tuple[int, int] | None = None
        self.hovered_cell: tuple[int, int] | None = None
        self.status_msg = ""
        self.status_timer = 0
        self.running = True

    def new_game(self):
        self.state = GameState()
        self.mode = C.MODE_MOVE
        self.wall_preview = None
        self.hovered_cell = None
        self.status_msg = ""
        self.status_timer = 0

    def set_status(self, msg: str, ms: int = 2500):
        self.status_msg = msg
        self.status_timer = ms

    def toggle_mode(self):
        if self.mode == C.MODE_MOVE:
            if self.state.walls_left[self.state.current_player] > 0:
                self.mode = C.MODE_WALL
            else:
                self.set_status("У вас не залишилося стінок!")
        else:
            self.mode = C.MODE_MOVE

    def handle_events(self):
        mx, my = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                k = event.key
                if k == pygame.K_F2:
                    self.new_game()
                elif k in (pygame.K_SPACE, pygame.K_TAB):
                    self.toggle_mode()
                elif k == pygame.K_m:
                    self.mode = C.MODE_MOVE
                elif k == pygame.K_w:
                    if self.state.walls_left[self.state.current_player] > 0:
                        self.mode = C.MODE_WALL
                    else:
                        self.set_status("У вас не залишилося стінок!")
                elif k == pygame.K_r:
                    self.wall_horizontal = not self.wall_horizontal
                elif k == pygame.K_ESCAPE:
                    self.mode = C.MODE_MOVE
                    self.wall_preview = None

            elif event.type == pygame.MOUSEBUTTONDOWN and self.state.winner is None:
                if event.button == 3:
                    self.mode = C.MODE_MOVE
                    self.wall_preview = None

                elif event.button == 1:
                    if self.renderer.toggle_btn_rect.collidepoint(mx, my):
                        self.toggle_mode()

                    elif self.mode == C.MODE_MOVE:
                        cell = BoardView.pixel_to_cell(mx, my)
                        if cell and cell in self.state.get_valid_moves():
                            self.state.move_pawn(*cell)

                    elif self.mode == C.MODE_WALL:
                        slot = WallView.pixel_to_wall_slot(mx, my, self.wall_horizontal)
                        if slot:
                            if self.state.place_wall(*slot, self.wall_horizontal):
                                self.mode = C.MODE_MOVE
                            else:
                                self.set_status("Недозволена позиція стінки!")

    def update(self, dt: int):
        mx, my = pygame.mouse.get_pos()
        self.renderer.update(dt)

        if self.mode == C.MODE_MOVE:
            self.hovered_cell = BoardView.pixel_to_cell(mx, my)
            self.wall_preview = None
        else:
            self.hovered_cell = None
            self.wall_preview = WallView.pixel_to_wall_slot(mx, my, self.wall_horizontal)

        if self.status_timer > 0:
            self.status_timer = max(0, self.status_timer - dt)
            if self.status_timer == 0:
                self.status_msg = ""

    def render(self):
        valid_moves = self.state.get_valid_moves() if self.state.winner is None else []
        path_p0 = self.state.shortest_path(0)
        path_p1 = self.state.shortest_path(1)

        self.renderer.draw_frame(
            gs=self.state,
            valid_moves=valid_moves,
            mode=self.mode,
            wall_preview=self.wall_preview,
            wall_horizontal=self.wall_horizontal,
            hovered_cell=self.hovered_cell,
            path_p0=path_p0,
            path_p1=path_p1,
            status_msg=self.status_msg,
        )
        pygame.display.flip()

    def run(self):
        while self.running:
            dt = self.clock.tick(60)
            self.handle_events()
            self.update(dt)
            self.render()

        pygame.quit()
        sys.exit()
