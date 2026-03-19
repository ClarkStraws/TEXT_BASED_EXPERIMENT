"""
Dialogue / NPC interaction renderer.
Fills the viewport area; sidebar shows ship stats as usual.
"""
import pygame
from typing import List
from config import SCREEN_W, SCREEN_H, SIDEBAR_W, LINE_H
from entities import NPC
from render_ship import ShipStats
from render_sidebar import draw_sidebar, SIDEBAR_X
from ui_console import ConsoleLog
from npc_data import NPCDialogue

VIEWPORT_W = SIDEBAR_X
VIEWPORT_H = SCREEN_H

_PAD = 18
_PORTRAIT_SIZE = 80


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


def draw_dialogue(
    screen: pygame.Surface,
    font: pygame.font.Font,
    npc: NPC,
    dialogue_state: str,
    ship_stats: ShipStats,
    log: ConsoleLog,
    npc_dialogue: NPCDialogue,
) -> None:
    # --- Background ---
    pygame.draw.rect(screen, (5, 8, 12), (0, 0, VIEWPORT_W, VIEWPORT_H))

    # === NPC HEADER PANEL ===
    header_h = _PORTRAIT_SIZE + _PAD * 2
    pygame.draw.rect(screen, (8, 14, 20), (0, 0, VIEWPORT_W, header_h))
    pygame.draw.line(screen, (35, 75, 95), (0, header_h), (VIEWPORT_W, header_h), 2)

    # Portrait circle
    px, py = _PAD + _PORTRAIT_SIZE // 2, _PAD + _PORTRAIT_SIZE // 2
    pygame.draw.circle(screen, (12, 20, 28), (px, py), _PORTRAIT_SIZE // 2)
    pygame.draw.circle(screen, npc.color, (px, py), _PORTRAIT_SIZE // 2, 2)
    # Icon letter
    icon = font.render(npc.name[0], True, npc.color)
    screen.blit(icon, (px - icon.get_width() // 2, py - icon.get_height() // 2))

    # NPC name + description
    tx = _PAD * 2 + _PORTRAIT_SIZE
    name_surf = font.render(npc.name, True, npc.color)
    screen.blit(name_surf, (tx, _PAD))
    desc_surf = font.render(npc.description, True, (130, 155, 170))
    screen.blit(desc_surf, (tx, _PAD + LINE_H + 4))

    # Range indicator
    range_surf = font.render("COMM: ACTIVE  //  RANGE: <100u", True, (70, 110, 90))
    screen.blit(range_surf, (tx, _PAD + LINE_H * 2 + 8))

    # === DIALOGUE TEXT AREA ===
    text_y = header_h + _PAD
    text_w = VIEWPORT_W - _PAD * 2

    # Determine what text to show
    if dialogue_state == "greeting":
        speaker = npc.name
        body = npc_dialogue.greeting
        prompt = "SPACE / ENTER  —  continue"
    elif dialogue_state == "response":
        speaker = npc.name
        body = npc.response_text
        prompt = "SPACE / ENTER  —  continue"
    elif dialogue_state == "farewell":
        speaker = npc.name
        body = npc_dialogue.farewell
        prompt = "SPACE / ENTER  —  end communication"
    else:
        speaker = None
        body = None
        prompt = None

    if speaker and body:
        spk_surf = font.render(f"[ {speaker} ]", True, npc.color)
        screen.blit(spk_surf, (_PAD, text_y))
        text_y += LINE_H + 6

        # Draw text box background
        box_h = VIEWPORT_H - text_y - 160
        pygame.draw.rect(screen, (8, 13, 18), (_PAD - 4, text_y - 4, text_w + 8, box_h))
        pygame.draw.rect(screen, (28, 45, 58), (_PAD - 4, text_y - 4, text_w + 8, box_h), 1)

        lines = _wrap(body, font, text_w)
        for line in lines:
            if text_y + LINE_H > text_y - 4 + box_h:
                break
            screen.blit(font.render(line, True, (195, 215, 225)), (_PAD, text_y))
            text_y += LINE_H

        # Prompt
        prompt_y = _PAD - 4 + (VIEWPORT_H - 160)
        p_surf = font.render(prompt, True, (80, 120, 140))
        screen.blit(p_surf, (_PAD, prompt_y))

    # === PLAYER CHOICES ===
    if dialogue_state == "choices":
        choices_y = header_h + _PAD
        spk_surf = font.render("[ YOU ]", True, (200, 220, 200))
        screen.blit(spk_surf, (_PAD, choices_y))
        choices_y += LINE_H + 6

        pygame.draw.rect(screen, (8, 13, 18), (_PAD - 4, choices_y - 4, text_w + 8, VIEWPORT_H - choices_y - _PAD))
        pygame.draw.rect(screen, (28, 45, 58), (_PAD - 4, choices_y - 4, text_w + 8, VIEWPORT_H - choices_y - _PAD), 1)

        for i, (choice_text, _) in enumerate(npc_dialogue.exchanges):
            key_col = (140, 200, 160)
            txt_col = (185, 210, 220)
            num_surf = font.render(f"[{i + 1}]", True, key_col)
            txt_surf = font.render(choice_text, True, txt_col)
            screen.blit(num_surf, (_PAD + 4, choices_y))
            screen.blit(txt_surf, (_PAD + 36, choices_y))
            choices_y += LINE_H + 4

        # Farewell option
        choices_y += 4
        pygame.draw.line(screen, (28, 45, 58), (_PAD, choices_y), (VIEWPORT_W - _PAD, choices_y), 1)
        choices_y += 8
        fw_num = font.render(f"[{len(npc_dialogue.exchanges) + 1}]", True, (180, 120, 100))
        fw_txt = font.render("End communication.", True, (155, 130, 120))
        screen.blit(fw_num, (_PAD + 4, choices_y))
        screen.blit(fw_txt, (_PAD + 36, choices_y))

    # --- Sidebar ---
    draw_sidebar(
        screen, font, ship_stats, log,
        "Star-8008",
        hints=["1-3  choose", f"{len(npc_dialogue.exchanges) + 1}  farewell", "ESC  close comm"],
    )
