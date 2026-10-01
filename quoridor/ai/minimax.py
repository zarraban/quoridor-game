from __future__ import annotations
from typing import Optional
from quoridor import constants as C
from quoridor.game_state import GameState
from quoridor.ai.evaluator import Evaluator


class MinimaxAgent:
    def __init__(self, depth: int = 2, evaluator: Optional[Evaluator] = None):
        self.depth = depth
        self.evaluator = evaluator if evaluator is not None else Evaluator()

    def _apply_action(self, state: GameState, action: tuple) -> bool:
        act_type, params = action
        if act_type == "move":
            return state.move_pawn(params[0], params[1])
        elif act_type == "wall":
            return state.place_wall(params[0], params[1], params[2])
        return False

    def _get_candidate_walls(self, state: GameState, player: int) -> list[tuple]:
        if state.walls_left[player] <= 0:
            return []

        opp_player = 1 - player
        opp_path = state.shortest_path(opp_player)
        candidates = set()

        if len(opp_path) >= 2:
            for i in range(len(opp_path) - 1):
                r1, c1 = opp_path[i]
                r2, c2 = opp_path[i + 1]
                if r1 != r2:
                    mr = min(r1, r2)
                    for col in (c1, c1 - 1):
                        if 0 <= mr < C.BOARD_SIZE - 1 and 0 <= col < C.BOARD_SIZE - 1:
                            candidates.add((mr, col, True))
                if c1 != c2:
                    mc = min(c1, c2)
                    for row in (r1, r1 - 1):
                        if 0 <= row < C.BOARD_SIZE - 1 and 0 <= mc < C.BOARD_SIZE - 1:
                            candidates.add((row, mc, False))

        opr, opc = state.pawns[opp_player]
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                wr, wc = opr + dr, opc + dc
                if 0 <= wr < C.BOARD_SIZE - 1 and 0 <= wc < C.BOARD_SIZE - 1:
                    candidates.add((wr, wc, True))
                    candidates.add((wr, wc, False))

        valid_walls = []
        base_opp_dist = len(opp_path) - 1 if opp_path else 100

        for r, c, h in candidates:
            if state.can_place_wall(r, c, h):
                state.h_walls.add((r, c)) if h else state.v_walls.add((r, c))
                new_path = state.shortest_path(opp_player)
                new_dist = len(new_path) - 1 if new_path else 100
                state.h_walls.discard((r, c)) if h else state.v_walls.discard((r, c))

                impact = new_dist - base_opp_dist
                valid_walls.append(((r, c, h), impact))

        valid_walls.sort(key=lambda x: x[1], reverse=True)
        return [w[0] for w in valid_walls[:12]]

    def get_candidate_actions(self, state: GameState, player: int) -> list[tuple]:
        actions = []
        goal_row = 0 if player == 0 else C.BOARD_SIZE - 1

        moves = state.get_valid_moves(player)
        moves.sort(key=lambda m: abs(m[0] - goal_row))
        for m in moves:
            actions.append(("move", m))

        walls = self._get_candidate_walls(state, player)
        for w in walls:
            actions.append(("wall", w))

        return actions

    def minimax(self, state: GameState, depth: int, alpha: float, beta: float,
                is_maximizing: bool, ai_player: int) -> float:
        if depth == 0 or state.winner is not None:
            return self.evaluator.evaluate(state, ai_player)

        curr_player = ai_player if is_maximizing else 1 - ai_player
        actions = self.get_candidate_actions(state, curr_player)

        if not actions:
            return self.evaluator.evaluate(state, ai_player)

        if is_maximizing:
            max_eval = -float('inf')
            for action in actions:
                next_state = state.copy()
                if not self._apply_action(next_state, action):
                    continue
                eval_score = self.minimax(next_state, depth - 1, alpha, beta, False, ai_player)
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for action in actions:
                next_state = state.copy()
                if not self._apply_action(next_state, action):
                    continue
                eval_score = self.minimax(next_state, depth - 1, alpha, beta, True, ai_player)
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval

    def get_best_action(self, state: GameState, ai_player: int) -> Optional[tuple]:
        if state.winner is not None:
            return None

        actions = self.get_candidate_actions(state, ai_player)
        if not actions:
            return None

        best_action = None
        best_score = -float('inf')
        alpha = -float('inf')
        beta = float('inf')

        for action in actions:
            next_state = state.copy()
            if not self._apply_action(next_state, action):
                continue
            score = self.minimax(next_state, self.depth - 1, alpha, beta, False, ai_player)
            if score > best_score:
                best_score = score
                best_action = action
            alpha = max(alpha, score)

        return best_action
