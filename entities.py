from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional

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