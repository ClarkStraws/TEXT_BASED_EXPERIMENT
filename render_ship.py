import pygame
from config import SCREEN_W, SCREEN_H, SIDEBAR_W, FONT_SIZE, LINE_H
from dataclasses import dataclass


# ----------------------------
# Ship stats (resource model)
# ----------------------------
@dataclass
class ShipStats:
    food: int = 25
    water: int = 30
    fuel: int = 80
    fuel_max: int = 100
    credits: int = 120
    hull_hp: int = 85
    hull_hp_max: int = 100
    shield_hp: int = 55
    shield_hp_max: int = 75
    cargo_weight: int = 0
    cargo_cap: int = 120


def draw_bar(surface: pygame.Surface, rect: pygame.Rect,
             value: int, max_value: int,
             color: tuple = (120, 220, 255)) -> None:
    pygame.draw.rect(surface, (20, 25, 30), rect)
    pygame.draw.rect(surface, (40, 55, 65), rect, 1)
    if max_value <= 0:
        return
    fill_w = int(rect.width * max(0.0, min(1.0, value / max_value)))
    if fill_w > 0:
        pygame.draw.rect(surface, color, pygame.Rect(rect.x, rect.y, fill_w, rect.height))
