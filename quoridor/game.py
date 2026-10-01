from __future__ import annotations
import sys
import pygame
from quoridor import constants as C
from quoridor.game_state import GameState
from quoridor.board_view import BoardView
from quoridor.pieces import WallView
from quoridor.renderer import Renderer
from quoridor.ai.minimax import MinimaxAgent


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

        self.game_mode = C.GAME_MODE_BOT
        self.ai_agent = MinimaxAgent(depth=2)

        self.state = GameState()
        self.mode = C.MODE_MOVE
        self.wall_horizontal = True
        self.wall_preview: tuple[int, int] | None = None
        self.hovered_cell: tuple[int, int] | None = None
        self.status_msg = ""
        self.status_timer = 0
        self.bot_thinking = False
        self.bot_think_timer = 0
        self.running = True

    def new_game(self):
        self.state = GameState()
        self.mode = C.MODE_MOVE
        self.wall_preview = None
        self.hovered_cell = None
        self.status_msg = ""
        self.status_timer = 0
        self.bot_thinking = False
        self.bot_think_timer = 0

    def switch_game_mode(self, new_mode: str):
        if self.game_mode != new_mode:
            self.game_mode = new_mode
            self.new_game()
            mode_str = "1 VS 1" if new_mode == C.GAME_MODE_PVP else "VS BOT"
            self.set_status(f"Режим змінено: {mode_str}")

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
        is_bot_turn = (self.game_mode == C.GAME_MODE_BOT and
                       self.state.current_player == 1 and
                       self.state.winner is None)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                k = event.key
                if k == pygame.K_F1:
                    new_mode = C.GAME_MODE_BOT if self.game_mode == C.GAME_MODE_PVP else C.GAME_MODE_PVP
                    self.switch_game_mode(new_mode)
                elif k == pygame.K_F2:
                    self.new_game()
                elif k in (pygame.K_SPACE, pygame.K_TAB):
                    if not is_bot_turn:
                        self.toggle_mode()
                elif k == pygame.K_m:
                    if not is_bot_turn:
                        self.mode = C.MODE_MOVE
                elif k == pygame.K_w:
                    if not is_bot_turn:
                        if self.state.walls_left[self.state.current_player] > 0:
                            self.mode = C.MODE_WALL
                        else:
                            self.set_status("У вас не залишилося стінок!")
                elif k == pygame.K_r:
                    self.wall_horizontal = not self.wall_horizontal
                elif k == pygame.K_ESCAPE:
                    self.mode = C.MODE_MOVE
                    self.wall_preview = None

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.renderer.pvp_btn_rect.collidepoint(mx, my):
                        self.switch_game_mode(C.GAME_MODE_PVP)
                        return
                    elif self.renderer.bot_btn_rect.collidepoint(mx, my):
                        self.switch_game_mode(C.GAME_MODE_BOT)
                        return

                if is_bot_turn or self.state.winner is not None:
                    continue

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

        is_bot_turn = (self.game_mode == C.GAME_MODE_BOT and
                       self.state.current_player == 1 and
                       self.state.winner is None)

        if is_bot_turn:
            self.hovered_cell = None
            self.wall_preview = None
            if not self.bot_thinking:
                self.bot_thinking = True
                self.bot_think_timer = 250
            else:
                self.bot_think_timer -= dt
                if self.bot_think_timer <= 0:
                    action = self.ai_agent.get_best_action(self.state, ai_player=1)
                    if action:
                        act_type, params = action
                        if act_type == "move":
                            self.state.move_pawn(*params)
                        elif act_type == "wall":
                            self.state.place_wall(*params)
                    self.bot_thinking = False
        else:
            self.bot_thinking = False
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
            game_mode=self.game_mode,
            wall_preview=self.wall_preview,
            wall_horizontal=self.wall_horizontal,
            hovered_cell=self.hovered_cell,
            path_p0=path_p0,
            path_p1=path_p1,
            status_msg=self.status_msg,
            is_bot_thinking=self.bot_thinking,
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
