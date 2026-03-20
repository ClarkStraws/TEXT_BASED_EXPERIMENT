import pygame
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional
from entities import GameObj, Player
from world import TILES, OBJECTS, find_spawn, obj_at, is_blocked
from ui_console import ConsoleLog
from render_world import draw_world, draw_sidebar_world
from render_ship import draw_ship_hub, ShipStats
from game_state import STATE_WORLD, STATE_SHIP, STATE_DIALOGUE, STATE_DUNGEON
from config import SCREEN_W, SCREEN_H, GRID_W, GRID_H, TILE_SIZE, SIDEBAR_W, FONT_SIZE, FPS
from input import movement_from_key
from world import make_empty_map, carve_border_walls, scatter_patches, place_objects, save_map


def try_move_player(player: Player, dx: int, dy: int, tilemap: List[List[str]], objs: List[GameObj], log: ConsoleLog) -> None:
    nx, ny = player.x + dx, player.y + dy

    # Door interaction: bump door -> turn into item (non-blocking) as a simple demo
    o = obj_at(objs, nx, ny)
    if o and o.kind == "door":
        log.add("You open the door.")
        o.kind = "item"
        return

    if is_blocked(tilemap, objs, nx, ny):
        o2 = obj_at(objs, nx, ny)
        if 0 <= ny < len(tilemap) and 0 <= nx < len(tilemap[0]) and not TILES[tilemap[ny][nx]].walkable:
            log.add(f"You bump into {TILES[tilemap[ny][nx]].name}.")
        elif o2 and OBJECTS[o2.kind].blocks:
            log.add(f"You bump into {OBJECTS[o2.kind].name}.")
        else:
            log.add("You can't go that way.")
        return

    player.x, player.y = nx, ny

    # Pick up item
    o3 = obj_at(objs, player.x, player.y)
    if o3 and o3.kind == "item":
        log.add("You pick up an item.")
        objs.remove(o3)



def main() -> None:
    pygame.init()
    pygame.display.set_caption("Grid Roguelike Starter + Ship Hub (P to board/exit)")
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", FONT_SIZE)

    log = ConsoleLog()
    log.add("Welcome.")
    log.add("Move with WASD or Arrow keys.")
    log.add("Press P while standing on the ship to board it.")

    # Build world
    tilemap = make_empty_map(GRID_W, GRID_H, "floor")
    carve_border_walls(tilemap)
    scatter_patches(tilemap, "grass", count=8, patch_size=22)
    scatter_patches(tilemap, "sand",  count=6, patch_size=18)
    scatter_patches(tilemap, "water", count=5, patch_size=14)

    objs = place_objects(tilemap, num=18)

    # Place a ship somewhere walkable
    sx, sy = find_spawn(tilemap, objs)
    ship_obj = GameObj(kind="ship", x=sx, y=sy)
    objs.append(ship_obj)
    log.add(f"A spaceship has landed at ({sx}, {sy}).")

    # Save map to file for debugging/demo purposes. 
    #save_map(tilemap, objs, "project-python/TEXT_BASED_EXPERIMENT/data/saved_map.txt")  

    # Player spawn (not on ship)
    px, py = find_spawn(tilemap, objs)
    player = Player(px, py)

    ship_stats = ShipStats()
    state = STATE_WORLD

    running = True
    while running:
        # --- Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                # Toggle between world and ship with P
                if event.key == pygame.K_p:
                    if state == STATE_WORLD:
                        # only board if standing on ship
                        o = obj_at(objs, player.x, player.y)
                        if o and o.kind == "ship":
                            state = STATE_SHIP
                            log.add("You board the spaceship.")
                        else:
                            log.add("You need to stand on the ship to board it. (Press P)")
                    else:
                        state = STATE_WORLD
                        log.add("You exit the spaceship back to the world.")
                    continue

                # World movement only in world state
                if state == STATE_WORLD:
                    dx, dy = movement_from_key(event.key)
                    if dx or dy:
                        try_move_player(player, dx, dy, tilemap, objs, log)

                    # Demo: regenerate world
                    elif event.key == pygame.K_r:
                        log.add("Regenerating world (R).")
                        tilemap = make_empty_map(GRID_W, GRID_H, "floor")
                        carve_border_walls(tilemap)
                        scatter_patches(tilemap, "grass", count=8, patch_size=22)
                        scatter_patches(tilemap, "sand",  count=6, patch_size=18)
                        scatter_patches(tilemap, "water", count=5, patch_size=14)
                        objs = place_objects(tilemap, num=18)
                        # Keep ship and place it
                        sx, sy = find_spawn(tilemap, objs)
                        ship_obj = GameObj(kind="ship", x=sx, y=sy)
                        objs.append(ship_obj)
                        player.x, player.y = find_spawn(tilemap, objs)
                        log.add(f"A spaceship has landed at ({sx}, {sy}).")

        # --- Render
        screen.fill((0, 0, 0))

        if state == STATE_WORLD:
            draw_world(screen, tilemap, objs, player)
            draw_sidebar_world(screen, font, log, tilemap, objs, player)
        else:
            draw_ship_hub(screen, font, ship_stats)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()