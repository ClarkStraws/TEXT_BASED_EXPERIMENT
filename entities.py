from dataclasses import dataclass, field
from typing import List, Tuple, Any, Optional


@dataclass
class GameObj:
    kind: str
    x: int
    y: int


@dataclass
class Player:
    x: int
    y: int
    color: Tuple[int, int, int] = (220, 220, 220)


@dataclass
class Planet:
    name: str
    x: float
    y: float
    type: str
    size: float
    habitable: bool
    color: Tuple[int, int, int]


@dataclass
class Star:
    name: str
    x: float
    y: float
    classification: str  # O | B | A | F | G | K | M
    color: Tuple[int, int, int]


@dataclass
class SolarSystem:
    star_system: List[Star]
    planets: List[Planet]


@dataclass
class ShipPlayer:
    """Player's ship in solar system space. Coordinates are world-space pixels."""
    x: float = -300.0
    y: float = 0.0
    angle: float = 270.0  # degrees; 0=right, 90=down, 180=left, 270=up


@dataclass
class NPC:
    """An NPC contact in a solar system."""
    name: str
    x: float
    y: float
    description: str
    color: Tuple[int, int, int]
    dialogue: Any  # NPCDialogue object from npc_data
    response_text: str = field(default="")
