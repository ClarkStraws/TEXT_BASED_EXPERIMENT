import pygame
from typing import List
from entities import GameObj, Player
from config import TILE_SIZE, GRID_W, GRID_H, SIDEBAR_W, SCREEN_H, LINE_H
from ui_console import ConsoleLog
from world import TILES, OBJECTS, obj_at
# ----------------------------
# Rendering: World
# ----------------------------
def draw_world(screen: pygame.Surface, tilemap: List[List[str]], objs: List[GameObj], player: Player) -> None:
    # Tiles
    for y, row in enumerate(tilemap):
        for x, t in enumerate(row):
            td = TILES[t]
            r = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, td.color, r)

    # Grid lines
    grid_color = (20, 20, 20)
    for x in range(GRID_W + 1):
        pygame.draw.line(screen, grid_color, (x * TILE_SIZE, 0), (x * TILE_SIZE, GRID_H * TILE_SIZE), 1)
    for y in range(GRID_H + 1):
        pygame.draw.line(screen, grid_color, (0, y * TILE_SIZE), (GRID_W * TILE_SIZE, y * TILE_SIZE), 1)

    # Objects
    for o in objs:
        od = OBJECTS[o.kind]
        cx = o.x * TILE_SIZE + TILE_SIZE // 2
        cy = o.y * TILE_SIZE + TILE_SIZE // 2
        if od.shape == "circle":
            pygame.draw.circle(screen, od.color, (cx, cy), TILE_SIZE // 3)
        else:
            rect = pygame.Rect(o.x * TILE_SIZE + 5, o.y * TILE_SIZE + 5, TILE_SIZE - 10, TILE_SIZE - 10)
            pygame.draw.rect(screen, od.color, rect)

        # quick label for ship
        if o.kind == "ship":
            # small "▲" triangle-ish marker
            pygame.draw.polygon(
                screen,
                (10, 20, 25),
                [(cx, cy - 6), (cx - 6, cy + 6), (cx + 6, cy + 6)]
            )

    # Player
    pr = pygame.Rect(player.x * TILE_SIZE + 4, player.y * TILE_SIZE + 4, TILE_SIZE - 8, TILE_SIZE - 8)
    pygame.draw.rect(screen, player.color, pr)

# ----------------------------
# Rendering: Sidebar (world view)
# ----------------------------
def draw_sidebar_world(screen: pygame.Surface, font: pygame.font.Font, log: ConsoleLog,
                       tilemap: List[List[str]], objs: List[GameObj], player: Player) -> None:
    sidebar_x = GRID_W * TILE_SIZE
    sidebar_rect = pygame.Rect(sidebar_x, 0, SIDEBAR_W, SCREEN_H)
    pygame.draw.rect(screen, (15, 15, 15), sidebar_rect)

    title = font.render("WORLD", True, (230, 230, 230))
    screen.blit(title, (sidebar_x + 16, 12))

    status_y = 40
    under = TILES[tilemap[player.y][player.x]].name
    o = obj_at(objs, player.x, player.y)
    on = OBJECTS[o.kind].name if o else "(none)"

    status_lines = [
        f"Pos: ({player.x}, {player.y})",
        f"Tile: {under}",
        f"Here: {on}",
        "",
        "Hotkeys:",
        "  P = board/exit ship",
    ]

    for i, s in enumerate(status_lines):
        surf = font.render(s, True, (190, 190, 190))
        screen.blit(surf, (sidebar_x + 16, status_y + i * LINE_H))

    pygame.draw.line(screen, (40, 40, 40),
                     (sidebar_x + 16, 190),
                     (sidebar_x + SIDEBAR_W - 16, 190), 1)

    # Console area
    log_top = 200
    log_area_rect = pygame.Rect(sidebar_x + 16, log_top, SIDEBAR_W - 32, SCREEN_H - log_top - 16)
    pygame.draw.rect(screen, (10, 10, 10), log_area_rect)
    pygame.draw.rect(screen, (40, 40, 40), log_area_rect, 1)

    old_clip = screen.get_clip()
    screen.set_clip(log_area_rect)

    lines = log.last((log_area_rect.height // LINE_H) - 1)
    for i, line in enumerate(lines):
        surf = font.render(line, True, (210, 210, 210))
        screen.blit(surf, (log_area_rect.x + 6, log_area_rect.y + 6 + i * LINE_H))

    screen.set_clip(old_clip)