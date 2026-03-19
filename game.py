"""
Void Horizons — main entry point.

States:
  STATE_SOLAR_SYSTEM  fly your ship around the current solar system
  STATE_GALAXY        full galaxy map; select a system and jump to it
  STATE_DIALOGUE      comm channel with an NPC contact
"""
import math
import os
import pygame
from typing import List, Optional

from config import SCREEN_W, SCREEN_H, FPS, FONT_SIZE
from entities import ShipPlayer, NPC, SolarSystem
from game_state import STATE_GALAXY, STATE_SOLAR_SYSTEM, STATE_DIALOGUE
from ui_console import ConsoleLog
from render_ship import ShipStats
from render_galaxy import draw_galaxy_map
from render_system_view import draw_system_view
from render_dialogue import draw_dialogue
from galaxy_data import GALAXY_SYSTEMS, FUEL_PER_JUMP
from npc_data import ARIA_DIALOGUE
from render_solar_system import load_solar_system


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_system(system_info: dict) -> SolarSystem:
    """Load a SolarSystem from the system_info dict (may use a data file or stub)."""
    data_file = system_info.get("data_file")
    if data_file:
        # Resolve relative to this file's directory
        here = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(here, data_file)
        return load_solar_system(path)
    # Stub: return a minimal SolarSystem for display-only systems
    from entities import Star, Planet
    stub_star = Star(
        name=system_info["name"],
        x=0.0, y=0.0,
        classification=system_info["classification"],
        color=system_info["color"],
    )
    return SolarSystem(star_system=[stub_star], planets=[])


def _build_npcs_for_system(system_idx: int) -> List[NPC]:
    """Return NPC contacts for the given system index."""
    if system_idx == 0:  # Star-8008 — ARIA-4 is here
        return [NPC(
            name=ARIA_DIALOGUE.npc_name,
            x=180.0,
            y=-140.0,
            description=ARIA_DIALOGUE.npc_description,
            color=ARIA_DIALOGUE.npc_color,
            dialogue=ARIA_DIALOGUE,
            response_text="",
        )]
    return []


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    pygame.init()
    pygame.display.set_caption("Void Horizons")
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", FONT_SIZE)

    # -- Game state --
    state = STATE_SOLAR_SYSTEM
    current_system_idx = 0
    galaxy_cursor_idx = 0

    # -- Ship & resources --
    ship = ShipPlayer(x=-300.0, y=0.0, angle=270.0)
    ship_stats = ShipStats(
        food=25, water=30,
        fuel=80, fuel_max=100,
        credits=120,
        hull_hp=85, hull_hp_max=100,
        shield_hp=55, shield_hp_max=75,
        cargo_weight=0, cargo_cap=120,
    )

    # -- Solar system data --
    solar_system = _load_system(GALAXY_SYSTEMS[current_system_idx])
    npcs: List[NPC] = _build_npcs_for_system(current_system_idx)

    # -- Dialogue --
    active_npc: Optional[NPC] = None
    # dialogue_stage: "greeting" | "choices" | "response" | "farewell"
    dialogue_stage = "greeting"

    # -- Log --
    log = ConsoleLog()
    log.add("Systems online. Welcome, Captain.")
    log.add("You are in the Star-8008 system.")
    log.add("Press G to open the galaxy map.")
    log.add("Press E near a contact to hail them.")

    # -- Resource tick --
    resource_timer = 0.0
    RESOURCE_INTERVAL = 12.0  # seconds between consumption ticks

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        # -- Resource consumption over time --
        resource_timer += dt
        if resource_timer >= RESOURCE_INTERVAL:
            resource_timer = 0.0
            if ship_stats.food > 0:
                ship_stats.food -= 1
            if ship_stats.water > 0:
                ship_stats.water -= 1

        # ==============================================================
        # Event handling
        # ==============================================================
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                continue

            if event.type != pygame.KEYDOWN:
                continue

            key = event.key

            # ---- Global ESC ----
            if key == pygame.K_ESCAPE:
                if state == STATE_DIALOGUE:
                    state = STATE_SOLAR_SYSTEM
                    active_npc = None
                    dialogue_stage = "greeting"
                    log.add("Comm channel closed.")
                elif state == STATE_GALAXY:
                    state = STATE_SOLAR_SYSTEM
                    log.add("Galaxy map closed.")
                else:
                    running = False
                continue

            # ---- Galaxy map toggle ----
            if key == pygame.K_g and state in (STATE_SOLAR_SYSTEM, STATE_GALAXY):
                if state == STATE_SOLAR_SYSTEM:
                    state = STATE_GALAXY
                    galaxy_cursor_idx = current_system_idx
                    log.add("Galaxy map opened.")
                else:
                    state = STATE_SOLAR_SYSTEM
                    log.add("Galaxy map closed.")
                continue

            # ==== GALAXY MAP ====
            if state == STATE_GALAXY:
                if key == pygame.K_TAB:
                    galaxy_cursor_idx = (galaxy_cursor_idx + 1) % len(GALAXY_SYSTEMS)

                elif key in (pygame.K_RETURN, pygame.K_SPACE):
                    if galaxy_cursor_idx == current_system_idx:
                        log.add("Already here.")
                    elif ship_stats.fuel < FUEL_PER_JUMP:
                        log.add(f"Insufficient fuel. Need {FUEL_PER_JUMP} units.")
                    else:
                        ship_stats.fuel -= FUEL_PER_JUMP
                        current_system_idx = galaxy_cursor_idx
                        target = GALAXY_SYSTEMS[current_system_idx]
                        log.add(f"Jumped to {target['name']}. Fuel: {ship_stats.fuel}.")
                        solar_system = _load_system(target)
                        npcs = _build_npcs_for_system(current_system_idx)
                        ship.x, ship.y = -300.0, 0.0
                        ship.angle = 270.0
                        state = STATE_SOLAR_SYSTEM
                continue

            # ==== DIALOGUE ====
            if state == STATE_DIALOGUE and active_npc is not None:
                dlg = active_npc.dialogue  # NPCDialogue

                if dialogue_stage in ("greeting", "response"):
                    # Any key advances to choices
                    if key in (pygame.K_RETURN, pygame.K_SPACE):
                        dialogue_stage = "choices"

                elif dialogue_stage == "farewell":
                    if key in (pygame.K_RETURN, pygame.K_SPACE):
                        state = STATE_SOLAR_SYSTEM
                        active_npc = None
                        dialogue_stage = "greeting"
                        log.add("Comm channel closed.")

                elif dialogue_stage == "choices":
                    # Number keys select exchanges; last key is farewell
                    choice_keys = [
                        pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4,
                        pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8,
                    ]
                    farewell_key_idx = len(dlg.exchanges)
                    for i, k in enumerate(choice_keys):
                        if key == k:
                            if i < len(dlg.exchanges):
                                active_npc.response_text = dlg.exchanges[i][1]
                                dialogue_stage = "response"
                            elif i == farewell_key_idx:
                                active_npc.response_text = dlg.farewell
                                dialogue_stage = "farewell"
                            break
                continue

            # ==== SOLAR SYSTEM — interact ====
            if state == STATE_SOLAR_SYSTEM:
                if key == pygame.K_e:
                    for npc in npcs:
                        dist = math.hypot(ship.x - npc.x, ship.y - npc.y)
                        if dist < 100:
                            active_npc = npc
                            active_npc.response_text = ""
                            dialogue_stage = "greeting"
                            state = STATE_DIALOGUE
                            log.add(f"Hailing {npc.name}...")
                            break
                    else:
                        log.add("No contacts in range. Approach a vessel or station.")

        # ==============================================================
        # Continuous ship movement (solar system only)
        # ==============================================================
        if state == STATE_SOLAR_SYSTEM:
            speed = 150.0 * dt  # pixels per second
            keys = pygame.key.get_pressed()
            moved = False

            if keys[pygame.K_w] or keys[pygame.K_UP]:
                ship.y -= speed
                ship.angle = 270.0
                moved = True
            elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
                ship.y += speed
                ship.angle = 90.0
                moved = True

            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                ship.x -= speed
                ship.angle = 180.0 if not (keys[pygame.K_w] or keys[pygame.K_s]) else ship.angle
                moved = True
            elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                ship.x += speed
                ship.angle = 0.0 if not (keys[pygame.K_w] or keys[pygame.K_s]) else ship.angle
                moved = True

            # Diagonal angle correction
            if (keys[pygame.K_w] or keys[pygame.K_UP]) and (keys[pygame.K_a] or keys[pygame.K_LEFT]):
                ship.angle = 225.0
            elif (keys[pygame.K_w] or keys[pygame.K_UP]) and (keys[pygame.K_d] or keys[pygame.K_RIGHT]):
                ship.angle = 315.0
            elif (keys[pygame.K_s] or keys[pygame.K_DOWN]) and (keys[pygame.K_a] or keys[pygame.K_LEFT]):
                ship.angle = 135.0
            elif (keys[pygame.K_s] or keys[pygame.K_DOWN]) and (keys[pygame.K_d] or keys[pygame.K_RIGHT]):
                ship.angle = 45.0

            # Slow fuel drain while flying
            if moved:
                # 1 fuel per 60 seconds of flight (very slow)
                resource_timer  # no extra drain for now

        # ==============================================================
        # NPC proximity check
        # ==============================================================
        near_npc: Optional[NPC] = None
        if state == STATE_SOLAR_SYSTEM:
            for npc in npcs:
                if math.hypot(ship.x - npc.x, ship.y - npc.y) < 100:
                    near_npc = npc
                    break

        # ==============================================================
        # Render
        # ==============================================================
        screen.fill((4, 6, 10))

        if state == STATE_GALAXY:
            draw_galaxy_map(
                screen, font,
                GALAXY_SYSTEMS, current_system_idx, galaxy_cursor_idx,
                ship_stats, log,
            )

        elif state == STATE_SOLAR_SYSTEM:
            draw_system_view(
                screen, font,
                solar_system, ship, npcs, near_npc,
                ship_stats, log,
                GALAXY_SYSTEMS[current_system_idx],
            )

        elif state == STATE_DIALOGUE and active_npc is not None:
            draw_dialogue(
                screen, font,
                active_npc, dialogue_stage,
                ship_stats, log,
                active_npc.dialogue,
            )

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
