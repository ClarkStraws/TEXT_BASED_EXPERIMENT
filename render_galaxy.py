"""
Galaxy map renderer.
Shows all star systems on a 2D map; player can select a destination and jump.
"""
import pygame
import random
import math
from typing import List, Dict, Any
from config import SCREEN_W, SCREEN_H, SIDEBAR_W, LINE_H
from render_ship import ShipStats
from render_sidebar import draw_sidebar, SIDEBAR_X
from ui_console import ConsoleLog

VIEWPORT_W = SIDEBAR_X
VIEWPORT_H = SCREEN_H

# Static starfield seed
_STAR_FIELD: List[tuple] = []
_SF_SEEDED = False


def _ensure_starfield() -> None:
    global _STAR_FIELD, _SF_SEEDED
    if _SF_SEEDED:
        return
    rng = random.Random(17)
    for _ in range(220):
        x = rng.randint(0, VIEWPORT_W - 1)
        y = rng.randint(0, VIEWPORT_H - 1)
        b = rng.randint(50, 180)
        r = rng.choice([1, 1, 1, 2])
        _STAR_FIELD.append((x, y, b, r))
    _SF_SEEDED = True


def _draw_starfield(screen: pygame.Surface) -> None:
    _ensure_starfield()
    for x, y, b, r in _STAR_FIELD:
        pygame.draw.circle(screen, (b, b, b), (x, y), r)


def _star_radius(classification: str) -> int:
    return {"O": 7, "B": 6, "A": 6, "F": 5, "G": 5, "K": 5, "M": 4}.get(classification, 4)


def draw_galaxy_map(
    screen: pygame.Surface,
    font: pygame.font.Font,
    systems: List[Dict[str, Any]],
    current_idx: int,
    cursor_idx: int,
    ship_stats: ShipStats,
    log: ConsoleLog,
) -> None:
    # --- Background ---
    pygame.draw.rect(screen, (4, 6, 10), (0, 0, VIEWPORT_W, VIEWPORT_H))
    _draw_starfield(screen)

    # --- Faint connection lines between nearby systems ---
    for i, a in enumerate(systems):
        for j, b in enumerate(systems):
            if j <= i:
                continue
            dist = math.hypot(a["gx"] - b["gx"], a["gy"] - b["gy"])
            if dist < 280:
                pygame.draw.line(screen, (18, 28, 36),
                                 (a["gx"], a["gy"]), (b["gx"], b["gy"]), 1)

    # --- Systems ---
    for i, sys in enumerate(systems):
        gx, gy = sys["gx"], sys["gy"]
        col = sys["color"]
        is_current = i == current_idx
        is_cursor = i == cursor_idx

        # Glow rings
        if is_current:
            pygame.draw.circle(screen, (70, 65, 30), (gx, gy), 18, 1)
            pygame.draw.circle(screen, (100, 90, 40), (gx, gy), 12, 1)
        if is_cursor:
            pulse_col = (50, 130, 170) if not is_current else (130, 120, 50)
            pygame.draw.circle(screen, pulse_col, (gx, gy), 16, 1)

        r = _star_radius(sys["classification"])
        if is_current:
            r += 2
        pygame.draw.circle(screen, col, (gx, gy), r)

        # Label
        name_col = (220, 235, 245) if is_cursor else (130, 155, 170)
        name_surf = font.render(sys["name"], True, name_col)
        screen.blit(name_surf, (gx + r + 6, gy - 9))
        cls_surf = font.render(sys["classification"] + "-class", True, (80, 100, 115))
        screen.blit(cls_surf, (gx + r + 6, gy + 5))

    # --- Player ship marker above current system ---
    csys = systems[current_idx]
    cx, cy = csys["gx"], csys["gy"] - _star_radius(csys["classification"]) - 14
    pts = [(cx, cy - 8), (cx - 5, cy + 2), (cx + 5, cy + 2)]
    pygame.draw.polygon(screen, (160, 215, 255), pts)

    # --- Title ---
    title = font.render("GALAXY MAP", True, (210, 230, 240))
    screen.blit(title, (16, 14))

    # --- Selected system info box ---
    sel = systems[cursor_idx]
    bx, by, bw, bh = 14, 42, 310, 84
    pygame.draw.rect(screen, (7, 12, 18), (bx, by, bw, bh))
    pygame.draw.rect(screen, (35, 75, 95), (bx, by, bw, bh), 1)

    sname = font.render(sel["name"], True, sel["color"])
    screen.blit(sname, (bx + 10, by + 8))
    # Word-wrap description
    desc = sel["description"]
    max_chars = 42
    d1 = desc[:max_chars]
    d2 = desc[max_chars:max_chars * 2]
    screen.blit(font.render(d1, True, (145, 168, 182)), (bx + 10, by + 28))
    if d2:
        screen.blit(font.render(d2, True, (145, 168, 182)), (bx + 10, by + 46))
    if cursor_idx == current_idx:
        already = font.render("< current location >", True, (200, 200, 100))
        screen.blit(already, (bx + 10, by + 64))
    else:
        cost = font.render(f"Jump cost: {20} fuel", True, (160, 175, 185))
        screen.blit(cost, (bx + 10, by + 64))

    # --- Bottom hints ---
    hints_text = [
        "TAB  cycle systems",
        "ENTER  jump to selected",
        "ESC / G  close map",
    ]
    for i, h in enumerate(hints_text):
        hs = font.render(h, True, (80, 105, 120))
        screen.blit(hs, (16, VIEWPORT_H - 14 - (len(hints_text) - i) * LINE_H))

    # --- Sidebar ---
    draw_sidebar(
        screen, font, ship_stats, log,
        systems[current_idx]["name"],
        hints=["G  close map", "TAB  cycle", "ENTER  jump"],
    )
