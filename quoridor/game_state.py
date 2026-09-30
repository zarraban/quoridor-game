from __future__ import annotations
from collections import deque
from typing import Optional
from quoridor.constants import BOARD_SIZE, WALLS_PER_PLAYER


class GameState:
    DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def __init__(self):
        self.pawns: list[tuple[int, int]] = [(8, 4), (0, 4)]
        self.walls_left: list[int] = [WALLS_PER_PLAYER, WALLS_PER_PLAYER]
        self.h_walls: set[tuple[int, int]] = set()
        self.v_walls: set[tuple[int, int]] = set()
        self.current_player: int = 0
        self.winner: Optional[int] = None

    def is_wall_between(self, r1: int, c1: int, r2: int, c2: int) -> bool:
        dr, dc = r2 - r1, c2 - c1
        if dr == -1:
            return (r2, c1) in self.h_walls or (r2, c1 - 1) in self.h_walls
        if dr == 1:
            return (r1, c1) in self.h_walls or (r1, c1 - 1) in self.h_walls
        if dc == -1:
            return (r1, c2) in self.v_walls or (r1 - 1, c2) in self.v_walls
        if dc == 1:
            return (r1, c1) in self.v_walls or (r1 - 1, c1) in self.v_walls
        return False

    def get_valid_moves(self, player: Optional[int] = None) -> list[tuple[int, int]]:
        if player is None:
            player = self.current_player
        pr, pc = self.pawns[player]
        opr, opc = self.pawns[1 - player]
        moves = []
        for dr, dc in self.DIRS:
            nr, nc = pr + dr, pc + dc
            if not (0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE):
                continue
            if self.is_wall_between(pr, pc, nr, nc):
                continue
            if (nr, nc) == (opr, opc):
                jnr, jnc = nr + dr, nc + dc
                if (0 <= jnr < BOARD_SIZE and 0 <= jnc < BOARD_SIZE
                        and not self.is_wall_between(nr, nc, jnr, jnc)):
                    moves.append((jnr, jnc))
                else:
                    for sdr, sdc in self.DIRS:
                        if (sdr, sdc) == (dr, dc) or (sdr, sdc) == (-dr, -dc):
                            continue
                        snr, snc = nr + sdr, nc + sdc
                        if (0 <= snr < BOARD_SIZE and 0 <= snc < BOARD_SIZE
                                and not self.is_wall_between(nr, nc, snr, snc)):
                            moves.append((snr, snc))
            else:
                moves.append((nr, nc))
        return moves

    def move_pawn(self, row: int, col: int) -> bool:
        if self.winner is not None:
            return False
        if (row, col) not in self.get_valid_moves():
            return False
        self.pawns[self.current_player] = (row, col)
        self._check_win()
        if self.winner is None:
            self.current_player = 1 - self.current_player
        return True

    def can_place_wall(self, r: int, c: int, horizontal: bool) -> bool:
        if self.walls_left[self.current_player] <= 0:
            return False
        if horizontal:
            if not (0 <= r < BOARD_SIZE - 1 and 0 <= c < BOARD_SIZE - 1):
                return False
            if (r, c) in self.h_walls:
                return False
            if (r, c - 1) in self.h_walls or (r, c + 1) in self.h_walls:
                return False
            if (r, c) in self.v_walls:
                return False
        else:
            if not (0 <= r < BOARD_SIZE - 1 and 0 <= c < BOARD_SIZE - 1):
                return False
            if (r, c) in self.v_walls:
                return False
            if (r - 1, c) in self.v_walls or (r + 1, c) in self.v_walls:
                return False
            if (r, c) in self.h_walls:
                return False
        self.h_walls.add((r, c)) if horizontal else self.v_walls.add((r, c))
        ok = self._path_exists(0) and self._path_exists(1)
        self.h_walls.discard((r, c)) if horizontal else self.v_walls.discard((r, c))
        return ok

    def place_wall(self, r: int, c: int, horizontal: bool) -> bool:
        if self.winner is not None:
            return False
        if not self.can_place_wall(r, c, horizontal):
            return False
        if horizontal:
            self.h_walls.add((r, c))
        else:
            self.v_walls.add((r, c))
        self.walls_left[self.current_player] -= 1
        self.current_player = 1 - self.current_player
        return True

    def _path_exists(self, player: int) -> bool:
        goal_row = 0 if player == 0 else BOARD_SIZE - 1
        start = self.pawns[player]
        visited = {start}
        queue = deque([start])
        while queue:
            r, c = queue.popleft()
            if r == goal_row:
                return True
            for dr, dc in self.DIRS:
                nr, nc = r + dr, c + dc
                if (0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE
                        and (nr, nc) not in visited
                        and not self.is_wall_between(r, c, nr, nc)):
                    visited.add((nr, nc))
                    queue.append((nr, nc))
        return False

    def shortest_path(self, player: int) -> list[tuple[int, int]]:
        goal_row = 0 if player == 0 else BOARD_SIZE - 1
        start = self.pawns[player]
        prev: dict[tuple, Optional[tuple]] = {start: None}
        queue = deque([start])
        found = None
        while queue and found is None:
            r, c = queue.popleft()
            if r == goal_row:
                found = (r, c)
                break
            for dr, dc in self.DIRS:
                nr, nc = r + dr, c + dc
                if (0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE
                        and (nr, nc) not in prev
                        and not self.is_wall_between(r, c, nr, nc)):
                    prev[(nr, nc)] = (r, c)
                    queue.append((nr, nc))
        if found is None:
            return []
        path = []
        cur: Optional[tuple] = found
        while cur is not None:
            path.append(cur)
            cur = prev[cur]
        return path[::-1]

    def _check_win(self):
        r0, _ = self.pawns[0]
        r1, _ = self.pawns[1]
        if r0 == 0:
            self.winner = 0
        elif r1 == BOARD_SIZE - 1:
            self.winner = 1

    def copy(self) -> "GameState":
        gs = GameState.__new__(GameState)
        gs.pawns = list(self.pawns)
        gs.walls_left = list(self.walls_left)
        gs.h_walls = set(self.h_walls)
        gs.v_walls = set(self.v_walls)
        gs.current_player = self.current_player
        gs.winner = self.winner
        return gs
