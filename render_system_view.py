"""
Solar system exploration renderer.
The player flies their ship through the system in real-time.
Coordinate system: world-space origin = star position.
Scale: SYSTEM_SCALE pixels per AU.
"""
import pygame
import random
import math
from typing import List, Optional, Tuple
from config import SCREEN_W, SCREEN_H, SIDEBAR_W, LINE_H
from entities import ShipPlayer, NPC, SolarSystem
from render_ship import ShipStats
from render_sidebar import draw_sidebar, SIDEBAR_X
from ui_console import ConsoleLog

VIEWPORT_W = SIDEBAR_X
VIEWPORT_H = SCREEN_H
SYSTEM_SCALE = 70  # pixels per AU

# Parallax star field
_SYS_STARS: List[Tuple[int, int, int, int]] = []  # wx, wy, brightness, size
_SYS_STARS_SEEDED = False


def _ensure_sys_stars() -> None:
    global _SYS_STARS, _SYS_STARS_SEEDED
    if _SYS_STARS_SEEDED:
        return
    rng = random.Random(99)
    for _ in range(180):
        wx = rng.randint(-2500, 2500)
        wy = rng.randint(-2500, 2500)
        b = rng.randint(55, 180)
        sz = rng.choice([1, 1, 1, 1, 2])
        _SYS_STARS.append((wx, wy, b, sz))
    _SYS_STARS_SEEDED = True


def world_to_screen(wx: float, wy: float, cam_x: float, cam_y: float) -> Tuple[int, int]:
    """Convert a world-space position to screen-space pixel position."""
    sx = int(wx - cam_x + VIEWPORT_W // 2)
    sy = int(wy - cam_y + VIEWPORT_H // 2)
    return sx, sy


def _draw_background(screen: pygame.Surface, cam_x: float, cam_y: float) -> None:
    _ensure_sys_stars()
    pygame.draw.rect(screen, (4, 6, 10), (0, 0, VIEWPORT_W, VIEWPORT_H))
    for wx, wy, b, sz in _SYS_STARS:
        # Parallax: stars drift at ~15% of camera movement
        sx = int((wx - cam_x * 0.15) % VIEWPORT_W)
        sy = int((wy - cam_y * 0.15) % VIEWPORT_H)
        pygame.draw.circle(screen, (b, b, b), (sx, sy), sz)


def _star_color_glow(classification: str) -> Tuple[tuple, int]:
    """Return (core_color, glow_radius) based on star class."""
    mapping = {
        "O": ((200, 220, 255), 28),
        "B": ((180, 200, 255), 26),
        "A": ((210, 220, 255), 24),
        "F": ((255, 255, 230), 22),
        "G": (( 255, 255, 180), 22),
        "K": ((255, 190, 100), 20),
        "M": ((255, 160, 80),  18),
    }
    return mapping.get(classification, ((255, 255, 255), 20))


def _draw_ship(screen: pygame.Surface, sx: int, sy: int,
               angle: float, color=(180, 215, 255), size=10) -> None:
    """Draw player ship as a triangle pointing in the movement direction."""
    rad = math.radians(angle)
    tip = (sx + size * math.sin(rad), sy - size * math.cos(rad))
    left = (sx + (size // 2) * math.sin(rad + math.pi * 0.75),
            sy - (size // 2) * math.cos(rad + math.pi * 0.75))
    right = (sx + (size // 2) * math.sin(rad - math.pi * 0.75),
             sy - (size // 2) * math.cos(rad - math.pi * 0.75))
    pygame.draw.polygon(screen, color, [tip, left, right])
    # Engine glow
    pygame.draw.circle(screen, (80, 140, 200), (sx, sy), 4)


def _draw_npc_ship(screen: pygame.Surface, sx: int, sy: int, color: tuple) -> None:
    """Draw NPC contact as a diamond shape."""
    d = 8
    pts = [(sx, sy - d), (sx + d, sy), (sx, sy + d), (sx - d, sy)]
    pygame.draw.polygon(screen, color, pts)
    pygame.draw.polygon(screen, (255, 255, 255), pts, 1)


def draw_system_view(
    screen: pygame.Surface,
    font: pygame.font.Font,
    solar_system: SolarSystem,
    ship: ShipPlayer,
    npcs: List[NPC],
    near_npc: Optional[NPC],
    ship_stats: ShipStats,
    log: ConsoleLog,
    system_info: dict,
) -> None:
    cam_x, cam_y = ship.x, ship.y

    # --- Background ---
    _draw_background(screen, cam_x, cam_y)

    # Clip all rendering to viewport
    viewport_clip = pygame.Rect(0, 0, VIEWPORT_W, VIEWPORT_H)

    # --- Orbit rings ---
    star_sx, star_sy = world_to_screen(0, 0, cam_x, cam_y)
    for planet in solar_system.planets:
        orbit_r = int(math.hypot(planet.x, planet.y) * SYSTEM_SCALE)
        if orbit_r > 0:
            pygame.draw.circle(screen, (22, 35, 44), (star_sx, star_sy), orbit_r, 1)

    # --- Star ---
    star = solar_system.star_system[0]
    _, glow_r = _star_color_glow(star.classification)
    # Outer glow
    glow_surf = pygame.Surface((glow_r * 4, glow_r * 4), pygame.SRCALPHA)
    pygame.draw.circle(glow_surf, (*star.color, 30),
                       (glow_r * 2, glow_r * 2), glow_r * 2)
    screen.blit(glow_surf, (star_sx - glow_r * 2, star_sy - glow_r * 2))
    pygame.draw.circle(screen, star.color, (star_sx, star_sy), glow_r // 2 + 4)
    # Star name
    sname = font.render(star.name, True, (200, 185, 145))
    screen.blit(sname, (star_sx + glow_r // 2 + 6, star_sy - 8))

    # --- Planets ---
    for planet in solar_system.planets:
        px, py = world_to_screen(planet.x * SYSTEM_SCALE, planet.y * SYSTEM_SCALE, cam_x, cam_y)
        r = max(4, int(planet.size * 3.5))
        if -r <= px <= VIEWPORT_W + r and -r <= py <= VIEWPORT_H + r:
            pygame.draw.circle(screen, planet.color, (px, py), r)
            pygame.draw.circle(screen, (255, 255, 255), (px, py), r, 1)
            pname = font.render(planet.name, True, (145, 168, 182))
            screen.blit(pname, (px + r + 4, py - 8))
            ptype = font.render(planet.type, True, (90, 110, 125))
            screen.blit(ptype, (px + r + 4, py + 6))

    # --- NPCs ---
    for npc in npcs:
        nx, ny = world_to_screen(npc.x, npc.y, cam_x, cam_y)
        if 0 <= nx <= VIEWPORT_W and 0 <= ny <= VIEWPORT_H:
            _draw_npc_ship(screen, nx, ny, npc.color)
            n_label = font.render(npc.name, True, npc.color)
            screen.blit(n_label, (nx + 14, ny - 8))

    # --- Player ship (always at viewport center) ---
    ship_sx = VIEWPORT_W // 2
    ship_sy = VIEWPORT_H // 2
    _draw_ship(screen, ship_sx, ship_sy, ship.angle)

    # --- Interaction prompt ---
    if near_npc is not None:
        prompt = font.render(f"E  —  Hail {near_npc.name}", True, (200, 230, 255))
        px = VIEWPORT_W // 2 - prompt.get_width() // 2
        pygame.draw.rect(screen, (10, 20, 30),
                         (px - 8, VIEWPORT_H - 48, prompt.get_width() + 16, 24))
        screen.blit(prompt, (px, VIEWPORT_H - 44))

    # --- System name watermark ---
    sys_label = font.render(system_info["name"], True, (35, 52, 64))
    screen.blit(sys_label, (10, 10))

    # --- World coords HUD (top-left) ---
    coord = font.render(f"x:{ship.x:+.0f}  y:{ship.y:+.0f}", True, (55, 75, 90))
    screen.blit(coord, (10, 26))

    # --- Sidebar ---
    draw_sidebar(
        screen, font, ship_stats, log,
        system_info["name"],
        hints=["WASD  fly", "G  galaxy map", "E  interact"],
    )
