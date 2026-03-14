import pygame
from typing import Tuple
# ----------------------------
# Movement / interactions
# ----------------------------
def movement_from_key(key: int) -> Tuple[int, int]:
    if key in (pygame.K_w, pygame.K_UP):
        return (0, -1)
    if key in (pygame.K_s, pygame.K_DOWN):
        return (0, 1)
    if key in (pygame.K_a, pygame.K_LEFT):
        return (-1, 0)
    if key in (pygame.K_d, pygame.K_RIGHT):
        return (1, 0)
    return (0, 0)