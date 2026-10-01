from __future__ import annotations
from quoridor.game_state import GameState


class Evaluator:
    def __init__(self, w_dist: float = 2.0, w_walls: float = 0.4):
        self.w_dist = w_dist
        self.w_walls = w_walls

    def evaluate(self, state: GameState, ai_player: int) -> float:
        if state.winner is not None:
            if state.winner == ai_player:
                return 10000.0
            return -10000.0

        human_player = 1 - ai_player

        ai_path = state.shortest_path(ai_player)
        human_path = state.shortest_path(human_player)

        ai_dist = len(ai_path) - 1 if ai_path else 100
        human_dist = len(human_path) - 1 if human_path else 100

        dist_diff = human_dist - ai_dist
        walls_diff = state.walls_left[ai_player] - state.walls_left[human_player]

        score = (self.w_dist * dist_diff) + (self.w_walls * walls_diff)
        return float(score)
