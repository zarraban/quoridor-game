import sys
import pygame
from quoridor import constants as C
from quoridor.game_state import GameState
from quoridor.renderer import Renderer, cell_rect


def pixel_to_cell(mx, my):
    for r in range(C.BOARD_SIZE):
        for c in range(C.BOARD_SIZE):
            if cell_rect(r, c).collidepoint(mx, my):
                return r, c
    return None


def pixel_to_wall_slot(mx, my, horizontal):
    bx = mx - C.BOARD_OFFSET_X
    by = my - C.BOARD_OFFSET_Y
    if not (-C.GAP <= bx <= C.BOARD_PX + C.GAP and -C.GAP <= by <= C.BOARD_PX + C.GAP):
        return None
    if horizontal:
        r = int((by - C.CELL) // C.STEP)
        c = int(bx // C.STEP)
        if 0 <= r < C.BOARD_SIZE - 1 and 0 <= c < C.BOARD_SIZE - 1:
            return r, c
    else:
        c = int((bx - C.CELL) // C.STEP)
        r = int(by // C.STEP)
        if 0 <= r < C.BOARD_SIZE - 1 and 0 <= c < C.BOARD_SIZE - 1:
            return r, c
    return None


def main():
    pygame.init()
    pygame.display.set_caption("Quoridor — Tactical Duel")

    icon = pygame.Surface((32, 32), pygame.SRCALPHA)
    pygame.draw.circle(icon, C.C_P1, (16, 16), 14)
    pygame.draw.circle(icon, (255, 255, 255), (16, 16), 14, 2)
    pygame.display.set_icon(icon)

    screen   = pygame.display.set_mode((C.WINDOW_W, C.WINDOW_H))
    clock    = pygame.time.Clock()
    renderer = Renderer(screen)

    gs              = GameState()
    mode            = C.MODE_MOVE
    wall_horizontal = True
    wall_preview    = None
    hovered_cell    = None
    status_msg      = ""
    status_timer    = 0

    def new_game():
        nonlocal gs, mode, wall_preview, hovered_cell, status_msg, status_timer
        gs = GameState()
        mode = C.MODE_MOVE
        wall_preview = None
        hovered_cell = None
        status_msg = ""
        status_timer = 0

    def set_status(msg, ms=2500):
        nonlocal status_msg, status_timer
        status_msg = msg
        status_timer = ms

    running = True
    while running:
        dt = clock.tick(60)
        mx, my = pygame.mouse.get_pos()

        renderer.update(dt)

        if mode == C.MODE_MOVE:
            hovered_cell = pixel_to_cell(mx, my)
            wall_preview = None
        else:
            hovered_cell = None
            wall_preview = pixel_to_wall_slot(mx, my, wall_horizontal)

        if status_timer > 0:
            status_timer = max(0, status_timer - dt)
            if status_timer == 0:
                status_msg = ""

        valid_moves = gs.get_valid_moves() if gs.winner is None else []
        path_p0 = gs.shortest_path(0)
        path_p1 = gs.shortest_path(1)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                k = event.key
                if k == pygame.K_F2:
                    new_game()
                elif k == pygame.K_m:
                    mode = C.MODE_MOVE
                elif k == pygame.K_w:
                    if gs.walls_left[gs.current_player] > 0:
                        mode = C.MODE_WALL
                    else:
                        set_status("No walls remaining!")
                elif k == pygame.K_r:
                    wall_horizontal = not wall_horizontal
                elif k == pygame.K_ESCAPE:
                    mode = C.MODE_MOVE
                    wall_preview = None

            elif event.type == pygame.MOUSEBUTTONDOWN and gs.winner is None:
                if event.button == 3:
                    mode = C.MODE_MOVE
                    wall_preview = None
                elif event.button == 1:
                    if mode == C.MODE_MOVE:
                        cell = pixel_to_cell(mx, my)
                        if cell and cell in valid_moves:
                            gs.move_pawn(*cell)
                    elif mode == C.MODE_WALL:
                        slot = pixel_to_wall_slot(mx, my, wall_horizontal)
                        if slot:
                            if gs.place_wall(*slot, wall_horizontal):
                                mode = C.MODE_MOVE
                            else:
                                set_status("Invalid wall position!")

        renderer.draw_frame(
            gs=gs,
            valid_moves=valid_moves,
            mode=mode,
            wall_preview=wall_preview,
            wall_horizontal=wall_horizontal,
            hovered_cell=hovered_cell,
            path_p0=path_p0,
            path_p1=path_p1,
            status_msg=status_msg,
        )
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
