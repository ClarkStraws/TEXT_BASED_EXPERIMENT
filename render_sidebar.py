"""
Shared sidebar renderer used by all game views.
"""
import pygame
from typing import List
from config import SCREEN_W, SCREEN_H, SIDEBAR_W, LINE_H
from render_ship import ShipStats, draw_bar

SIDEBAR_X = SCREEN_W - SIDEBAR_W
_INNER_W = SIDEBAR_W - 28  # usable width inside padding


def _wrap(text: str, font: pygame.font.Font, max_w: int) -> List[str]:
    words = text.split()
    lines: List[str] = []
    current = ""
    for word in words:
        test = (current + " " + word).strip()
        if font.size(test)[0] <= max_w:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_sidebar(
    screen: pygame.Surface,
    font: pygame.font.Font,
    ship_stats: ShipStats,
    log,
    system_name: str,
    hints: List[str],
) -> None:
    """Draw the right-side status panel shared across all game states."""
    sx = SIDEBAR_X
    x0 = sx + 14

    # Background + border
    pygame.draw.rect(screen, (6, 10, 14), (sx, 0, SIDEBAR_W, SCREEN_H))
    pygame.draw.line(screen, (35, 75, 95), (sx, 0), (sx, SCREEN_H), 2)

    y = 12

    def lbl(text: str, color=(160, 185, 200)) -> None:
        nonlocal y
        screen.blit(font.render(text, True, color), (x0, y))
        y += LINE_H

    def kv(key: str, val: str, val_color=(215, 230, 245)) -> None:
        nonlocal y
        k_surf = font.render(key, True, (120, 145, 160))
        v_surf = font.render(val, True, val_color)
        screen.blit(k_surf, (x0, y))
        screen.blit(v_surf, (sx + SIDEBAR_W - 14 - v_surf.get_width(), y))
        y += LINE_H

    def bar_row(label: str, cur: int, mx: int, color=(120, 220, 255)) -> None:
        nonlocal y
        screen.blit(font.render(label, True, (120, 145, 160)), (x0, y))
        frac = font.render(f"{cur}/{mx}", True, (100, 125, 140))
        screen.blit(frac, (sx + SIDEBAR_W - 14 - frac.get_width(), y))
        y += LINE_H - 4
        rect = pygame.Rect(x0, y, _INNER_W, 10)
        draw_bar(screen, rect, cur, mx, color)
        y += 16

    def divider() -> None:
        nonlocal y
        y += 5
        pygame.draw.line(screen, (28, 42, 52), (x0, y), (sx + SIDEBAR_W - 14, y), 1)
        y += 8

    # ---- Location ----
    lbl("LOCATION", (160, 185, 200))
    loc_surf = font.render(system_name, True, (255, 225, 130))
    screen.blit(loc_surf, (x0, y))
    y += LINE_H

    divider()

    # ---- Resources ----
    lbl("RESOURCES", (160, 185, 200))
    bar_row("Fuel", ship_stats.fuel, ship_stats.fuel_max, (80, 200, 255))
    kv("Food", str(ship_stats.food))
    kv("Water", str(ship_stats.water))
    kv("Credits", str(ship_stats.credits))
    kv("Cargo", f"{ship_stats.cargo_weight}/{ship_stats.cargo_cap}")

    divider()

    # ---- Status ----
    lbl("STATUS", (160, 185, 200))
    bar_row("Hull", ship_stats.hull_hp, ship_stats.hull_hp_max, (80, 210, 120))
    bar_row("Shield", ship_stats.shield_hp, ship_stats.shield_hp_max, (120, 170, 255))

    divider()

    # ---- Controls ----
    if hints:
        lbl("CONTROLS", (160, 185, 200))
        for h in hints:
            screen.blit(font.render(h, True, (90, 115, 130)), (x0, y))
            y += LINE_H
        divider()

    # ---- Log ----
    lbl("LOG", (160, 185, 200))
    log_lines = log.last(20)
    for line in log_lines:
        for wrapped_line in _wrap(line, font, _INNER_W):
            if y + LINE_H > SCREEN_H - 6:
                break
            screen.blit(font.render(wrapped_line, True, (100, 125, 140)), (x0, y))
            y += LINE_H
        if y + LINE_H > SCREEN_H - 6:
            break
