import math
import random
import pygame
import pygame.gfxdraw
from quoridor import constants as C


class ParticleSystem:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.particles: list[dict] = []
        self._bg_surf = self._build_background()
        self._init_particles()

    def _init_particles(self):
        for _ in range(35):
            self.particles.append(self._create_particle(random.randint(0, self.height)))

    def _create_particle(self, y: float | None = None) -> dict:
        return {
            "x": random.uniform(0, self.width),
            "y": y if y is not None else self.height,
            "vy": random.uniform(0.2, 0.7),
            "r": random.uniform(1.2, 2.8),
            "alpha": random.randint(40, 130),
            "color": random.choice([(90, 150, 255), (130, 210, 255), (210, 170, 255)]),
        }

    def _build_background(self) -> pygame.Surface:
        surf = pygame.Surface((self.width, self.height))
        for y in range(self.height):
            t = y / self.height
            r = int(C.C_BG_TOP[0] * (1 - t) + C.C_BG_BOT[0] * t)
            g = int(C.C_BG_TOP[1] * (1 - t) + C.C_BG_BOT[1] * t)
            b = int(C.C_BG_TOP[2] * (1 - t) + C.C_BG_BOT[2] * t)
            pygame.draw.line(surf, (r, g, b), (0, y), (self.width, y))

        mountain_color = (14, 18, 38)
        peaks = [
            (90, 310, 180), (270, 250, 140), (830, 330, 200),
            (970, 270, 160), (40, 190, 120), (690, 290, 170), (510, 170, 130)
        ]
        for mx, mh, mw in peaks:
            pts = [(mx - mw, self.height), (mx, self.height - mh), (mx + mw, self.height)]
            pygame.draw.polygon(surf, mountain_color, pts)

        for i in range(3):
            ax = 180 + i * 320
            aurora = pygame.Surface((320, 380), pygame.SRCALPHA)
            for y in range(380):
                alpha = int(14 * math.sin(y / 40) * (1 - y / 380))
                if alpha > 0:
                    col = [(60, 120, 255), (70, 190, 170), (170, 80, 255)][i]
                    pygame.draw.line(aurora, (*col, alpha), (0, y), (320, y))
            surf.blit(aurora, (ax, 0))

        return surf

    def update(self, dt: float):
        for i, p in enumerate(self.particles):
            p["y"] -= p["vy"]
            if p["y"] < 0:
                self.particles[i] = self._create_particle()

    def draw(self, surf: pygame.Surface):
        surf.blit(self._bg_surf, (0, 0))
        for p in self.particles:
            try:
                pygame.gfxdraw.filled_circle(
                    surf, int(p["x"]), int(p["y"]),
                    int(p["r"]), (*p["color"], p["alpha"])
                )
            except Exception:
                pass
