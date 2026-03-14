import pygame
import random
from config import *
from world import find_spawn, obj_at
from game_state import STATE_WORLD, STATE_SHIP
from dataclasses import dataclass
from render_solar_system import get_current_solar_system
from entities import SolarSystem, Star, Planet
# ----------------------------
# Ship (hub) stats
# ----------------------------
@dataclass
class ShipStats:
    food: int = 25
    water: int = 30
    credits: int = 120
    hull_hp: int = 85
    hull_hp_max: int = 100
    shield_hp: int = 55
    shield_hp_max: int = 75
    cargo_weight: int = 42
    cargo_cap: int = 120



# ----------------------------
# Rendering: Ship Hub UI
# ----------------------------
def draw_bar(screen: pygame.Surface, rect: pygame.Rect, value: int, max_value: int) -> None:
    pygame.draw.rect(screen, (25, 25, 25), rect)
    pygame.draw.rect(screen, (60, 60, 60), rect, 1)
    if max_value <= 0:
        return
    fill_w = int(rect.width * max(0.0, min(1.0, value / max_value)))
    if fill_w > 0:
        pygame.draw.rect(screen, (120, 220, 255), pygame.Rect(rect.x, rect.y, fill_w, rect.height))


def draw_solar_system_view(screen: pygame.Surface, play_rect: pygame.Rect, font: pygame.font.Font) -> None:
     # A “unique view” panel on the main ship area (fake window)
    window = pygame.Rect(330, 95, play_rect.width - 360, 260)
    pygame.draw.rect(screen, (8, 14, 18), window)
    pygame.draw.rect(screen, (40, 120, 140), window, 2)

    solar_system = get_current_solar_system()

    for star in solar_system.star_system:
        sx = int(window.left + window.width / 2)
        sy = int(window.top + window.height / 2)
        pygame.draw.circle(screen, [255, 255, 255], (sx, sy), 8)

    for planet in solar_system.planets:
        # Map planet's (x,y) in AU to window coordinates
        px = int(window.left + window.width / 2 + planet.x * 20)  # 20 pixels per AU
        py = int(window.top + window.height / 2 + planet.y * 20)
        pygame.draw.circle(screen, planet.color, (px, py), max(3, int(planet.size)))
        # draw orbit pattern
        pygame.draw.circle(screen, (40, 120, 140), (window.left + window.width // 2, window.top + window.height // 2), int(((planet.x ** 2 + planet.y ** 2) ** 0.5) * 10), 1)


    wtitle = font.render("VIEWPORT", True, (190, 210, 215))
    screen.blit(wtitle, (window.left + 10, window.top - 22))

    
def draw_ship_hub(screen: pygame.Surface, font: pygame.font.Font, stats: ShipStats) -> None:
    # Main playfield area becomes ship interior UI
    play_rect = pygame.Rect(0, 0, GRID_W * TILE_SIZE, SCREEN_H)
    sidebar_x = GRID_W * TILE_SIZE
    sidebar_rect = pygame.Rect(sidebar_x, 0, SIDEBAR_W, SCREEN_H)

    # Background
    pygame.draw.rect(screen, (6, 10, 14), play_rect)
    pygame.draw.rect(screen, (10, 12, 16), sidebar_rect)

    # Sci-fi frame lines
    pygame.draw.rect(screen, (40, 120, 140), play_rect, 2)
    pygame.draw.line(screen, (40, 120, 140), (0, 70), (play_rect.right, 70), 2)
    pygame.draw.line(screen, (30, 70, 85), (0, 140), (play_rect.right, 140), 1)

    # A “radar-ish” panel
    radar = pygame.Rect(30, 95, 260, 260)
    pygame.draw.rect(screen, (8, 14, 18), radar)
    pygame.draw.rect(screen, (40, 120, 140), radar, 2)
    cx, cy = radar.center
    for r in (40, 80, 120):
        pygame.draw.circle(screen, (25, 60, 70), (cx, cy), r, 1)
    pygame.draw.line(screen, (25, 60, 70), (radar.left, cy), (radar.right, cy), 1)
    pygame.draw.line(screen, (25, 60, 70), (cx, radar.top), (cx, radar.bottom), 1)
    # Some blips
    for bx, by in [(cx + 50, cy - 30), (cx - 70, cy + 40), (cx + 10, cy + 80)]:
        pygame.draw.circle(screen, (120, 220, 255), (bx, by), 3)

    # Left title
    title = font.render("SHIP HUB", True, (220, 240, 245))
    screen.blit(title, (30, 20))
    hint = font.render("Press P to exit to world", True, (170, 190, 200))
    screen.blit(hint, (30, 45))

    # Sidebar stats (hub screen stats)
    side_title = font.render("SYSTEMS", True, (220, 240, 245))
    screen.blit(side_title, (sidebar_x + 16, 12))

    x0 = sidebar_x + 16
    y = 46

    def label(s: str, yy: int):
        screen.blit(font.render(s, True, (190, 210, 215)), (x0, yy))

    def value(s: str, yy: int):
        screen.blit(font.render(s, True, (230, 240, 245)), (x0 + 170, yy))

    # Food / Water / Credits / Cargo
    label("Food", y);      value(str(stats.food), y); y += LINE_H
    label("Water", y);     value(str(stats.water), y); y += LINE_H
    label("Credits", y);   value(str(stats.credits), y); y += LINE_H
    label("Cargo", y);     value(f"{stats.cargo_weight}/{stats.cargo_cap}", y); y += LINE_H + 8

    pygame.draw.line(screen, (40, 40, 40), (x0, y), (sidebar_x + SIDEBAR_W - 16, y), 1)
    y += 12

    # Hull bar
    label("Hull", y); y += LINE_H
    hull_rect = pygame.Rect(x0, y, SIDEBAR_W - 32, 16)
    draw_bar(screen, hull_rect, stats.hull_hp, stats.hull_hp_max)
    y += 22
    screen.blit(font.render(f"{stats.hull_hp}/{stats.hull_hp_max}", True, (190, 210, 215)), (x0, y))
    y += LINE_H + 10

    # Shield bar
    label("Shield", y); y += LINE_H
    shield_rect = pygame.Rect(x0, y, SIDEBAR_W - 32, 16)
    draw_bar(screen, shield_rect, stats.shield_hp, stats.shield_hp_max)
    y += 22
    screen.blit(font.render(f"{stats.shield_hp}/{stats.shield_hp_max}", True, (190, 210, 215)), (x0, y))
    y += LINE_H + 10

    pygame.draw.line(screen, (40, 40, 40), (x0, y), (sidebar_x + SIDEBAR_W - 16, y), 1)
    y += 12

    draw_solar_system_view(screen, play_rect, font)

   