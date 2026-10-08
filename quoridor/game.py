import sys
import pygame
import threading
from quoridor import constants as C
from quoridor.game_state import GameState
from quoridor.renderer import Renderer
from quoridor.ai.minimax import MinimaxAgent


class Game:
    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode((C.WINDOW_W, C.WINDOW_H))
        pygame.display.set_caption("Quoridor: Tactical Duel")
        self.clock = pygame.time.Clock()
        self.renderer = Renderer(self.window)
        
        self.app_state = C.STATE_MENU
        self.game_mode = C.GAME_MODE_PVP
        self.target_wins = 1
        self.scores = [0, 0]

        self.gs = GameState()
        self.ui_mode = C.MODE_MOVE
        self.wall_horiz = True
        self.hover_cell = None
        self.status_msg = ""
        self.msg_timer = 0.0

        self.bot = MinimaxAgent(depth=2)
        self.bot_thinking = False
        self.bot_move_result = None

    def start_new_round(self):
        self.gs = GameState()
        self.ui_mode = C.MODE_MOVE
        self.wall_horiz = True
        self.hover_cell = None
        self.status_msg = ""
        self.bot_thinking = False
        self.bot_move_result = None

    def start_new_series(self):
        self.scores = [0, 0]
        self.start_new_round()
        self.app_state = C.STATE_PLAYING

    def run(self):
        while True:
            dt = self.clock.tick(60) / 1000.0

            self._handle_events()
            self._update(dt)
            self._draw()

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if self.app_state == C.STATE_MENU:
                self._handle_menu_events(event)
            else:
                self._handle_game_events(event)

    def _handle_menu_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            mv = self.renderer.menu_view

            if mv.btn_pvp.collidepoint(mx, my):
                self.game_mode = C.GAME_MODE_PVP
            elif mv.btn_bot.collidepoint(mx, my):
                self.game_mode = C.GAME_MODE_BOT
            elif mv.btn_w1.collidepoint(mx, my):
                self.target_wins = 1
            elif mv.btn_w3.collidepoint(mx, my):
                self.target_wins = 3
            elif mv.btn_w5.collidepoint(mx, my):
                self.target_wins = 5
            elif mv.btn_start.collidepoint(mx, my):
                self.start_new_series()

    def _handle_game_events(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.app_state = C.STATE_MENU
            return

        if self.gs.winner is not None:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.scores[self.gs.winner] += 1
                if self.scores[self.gs.winner] >= self.target_wins:
                    self.app_state = C.STATE_MENU
                else:
                    self.start_new_round()
            return

        if self.bot_thinking:
            return

        if event.type == pygame.MOUSEMOTION:
            self._update_hover(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self._handle_left_click(event.pos)
            elif event.button == 3:
                self.ui_mode = C.MODE_MOVE
        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_SPACE, pygame.K_m, pygame.K_w):
                if self.ui_mode == C.MODE_MOVE:
                    self.ui_mode = C.MODE_WALL
                else:
                    self.ui_mode = C.MODE_MOVE
                mx, my = pygame.mouse.get_pos()
                self._update_hover((mx, my))
            elif event.key == pygame.K_r and self.ui_mode == C.MODE_WALL:
                self.wall_horiz = not self.wall_horiz

    def _update_hover(self, pos: tuple[int, int]):
        mx, my = pos
        col = (mx - C.BOARD_OFFSET_X) // C.STEP
        row = (my - C.BOARD_OFFSET_Y) // C.STEP

        if 0 <= row < C.BOARD_SIZE and 0 <= col < C.BOARD_SIZE:
            self.hover_cell = (row, col)
        else:
            self.hover_cell = None

    def _handle_left_click(self, pos: tuple[int, int]):
        if self.renderer.hud.toggle_btn_rect.collidepoint(pos):
            if self.ui_mode == C.MODE_MOVE:
                self.ui_mode = C.MODE_WALL
            else:
                self.ui_mode = C.MODE_MOVE
            self._update_hover(pos)
            return

        if not self.hover_cell:
            return

        r, c = self.hover_cell
        if self.ui_mode == C.MODE_MOVE:
            self._attempt_move(r, c)
        elif self.ui_mode == C.MODE_WALL:
            if 0 <= r < C.BOARD_SIZE - 1 and 0 <= c < C.BOARD_SIZE - 1:
                self._attempt_wall(r, c, self.wall_horiz)

    def _attempt_move(self, r: int, c: int):
        if self.gs.move_pawn(r, c):
            self._post_move()
        else:
            self.show_message("Некоректний хід!")

    def _attempt_wall(self, r: int, c: int, is_h: bool):
        if self.gs.can_place_wall(r, c, is_h):
            self.gs.place_wall(r, c, is_h)
            self.ui_mode = C.MODE_MOVE
            self._post_move()
        else:
            self.show_message("Не можна ставити стінку тут (перекриває шлях)!")

    def _post_move(self):
        mx, my = pygame.mouse.get_pos()
        self._update_hover((mx, my))
        if self.game_mode == C.GAME_MODE_BOT and self.gs.winner is None and self.gs.current_player == 1:
            self.bot_thinking = True
            threading.Thread(target=self._bot_think_worker, daemon=True).start()

    def _bot_think_worker(self):
        best_action = self.bot.get_best_action(self.gs, 1)
        self.bot_move_result = best_action

    def show_message(self, text: str):
        self.status_msg = text
        self.msg_timer = 2.0

    def _update(self, dt: float):
        self.renderer.update(dt)
        if self.msg_timer > 0:
            self.msg_timer -= dt
            if self.msg_timer <= 0:
                self.status_msg = ""

        if self.bot_thinking and self.bot_move_result is not None:
            act_type, params = self.bot_move_result
            if act_type == "move":
                self.gs.move_pawn(params[0], params[1])
            else:
                self.gs.place_wall(params[0], params[1], params[2])
            
            self.bot_thinking = False
            self.bot_move_result = None
            
            mx, my = pygame.mouse.get_pos()
            self._update_hover((mx, my))

    def _draw(self):
        self.renderer.draw(
            app_state=self.app_state,
            gs=self.gs,
            mode=self.ui_mode,
            game_mode=self.game_mode,
            target_wins=self.target_wins,
            scores=self.scores,
            wall_horiz=self.wall_horiz,
            hover_cell=self.hover_cell,
            status_msg=self.status_msg,
            bot_thinking=self.bot_thinking
        )
        pygame.display.flip()
