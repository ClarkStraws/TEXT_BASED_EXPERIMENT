import random
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional
from entities import GameObj

# ----------------------------
# Tile definitions
# ----------------------------
@dataclass(frozen=True)
class TileDef:
    name: str
    walkable: bool
    color: Tuple[int, int, int]

TILES: Dict[str, TileDef] = {
    "floor": TileDef("Floor", True,  (40, 40, 40)),
    "sand":  TileDef("Sand",  True,  (90, 80, 40)),
    "grass": TileDef("Grass", True,  (30, 70, 35)),
    "water": TileDef("Water", False, (25, 60, 120)),
    "wall":  TileDef("Wall",  False, (90, 90, 90)),
}

# ----------------------------
# Object definitions
# ----------------------------
@dataclass
class ObjDef:
    name: str
    blocks: bool
    color: Tuple[int, int, int]
    shape: str  # "rect" | "circle"

OBJECTS: Dict[str, ObjDef] = {
    "boulder": ObjDef("Boulder", True,  (120, 110, 100), "circle"),
    "door":    ObjDef("Door",    True,  (140, 90, 30),   "rect"),
    "item":    ObjDef("Item",    False, (220, 220, 80),  "circle"),
    "ship":    ObjDef("Spaceship", False, (120, 220, 255), "rect"),
}

# ----------------------------
# World generation
# ----------------------------
def make_empty_map(w: int, h: int, default_tile: str = "floor") -> List[List[str]]:
    return [[default_tile for _ in range(w)] for _ in range(h)]

def carve_border_walls(tilemap: List[List[str]]) -> None:
    h = len(tilemap)
    w = len(tilemap[0])
    for y in range(h):
        for x in range(w):
            if x == 0 or y == 0 or x == w - 1 or y == h - 1:
                tilemap[y][x] = "wall"

def scatter_patches(tilemap: List[List[str]], tile_kind: str, count: int, patch_size: int) -> None:
    h = len(tilemap)
    w = len(tilemap[0])
    for _ in range(count):
        cx = random.randint(1, w - 2)
        cy = random.randint(1, h - 2)
        for _ in range(patch_size):
            x = max(1, min(w - 2, cx + random.randint(-2, 2)))
            y = max(1, min(h - 2, cy + random.randint(-2, 2)))
            if tilemap[y][x] != "wall":
                tilemap[y][x] = tile_kind

def place_objects(tilemap: List[List[str]], num: int) -> List[GameObj]:
    h = len(tilemap)
    w = len(tilemap[0])
    objs: List[GameObj] = []
    kinds = ["boulder", "door", "item"]
    tries = 0
    while len(objs) < num and tries < num * 40:
        tries += 1
        x = random.randint(1, w - 2)
        y = random.randint(1, h - 2)
        if not TILES[tilemap[y][x]].walkable:
            continue
        if any(o.x == x and o.y == y for o in objs):
            continue
        kind = random.choice(kinds)
        objs.append(GameObj(kind=kind, x=x, y=y))
    return objs

def obj_at(objs: List[GameObj], x: int, y: int) -> Optional[GameObj]:
    for o in objs:
        if o.x == x and o.y == y:
            return o
    return None

def is_blocked(tilemap: List[List[str]], objs: List[GameObj], x: int, y: int) -> bool:
    if y < 0 or y >= len(tilemap) or x < 0 or x >= len(tilemap[0]):
        return True
    if not TILES[tilemap[y][x]].walkable:
        return True
    o = obj_at(objs, x, y)
    if o and OBJECTS[o.kind].blocks:
        return True
    return False

def find_spawn(tilemap: List[List[str]], objs: List[GameObj]) -> Tuple[int, int]:
    h = len(tilemap)
    w = len(tilemap[0])
    for _ in range(5000):
        x = random.randint(1, w - 2)
        y = random.randint(1, h - 2)
        if TILES[tilemap[y][x]].walkable and not any(o.x == x and o.y == y and OBJECTS[o.kind].blocks for o in objs):
            return x, y
    return 2, 2

# ----------------------------
# Save map and objects to file (for debugging)
# ----------------------------
def save_map(tilemap: List[List[str]], objs: List[GameObj], filename: str) -> None:
    with open(filename, "w") as f:
        for y in range(len(tilemap)):
            for x in range(len(tilemap[0])):
                o = obj_at(objs, x, y)
                if o:
                    f.write(f"{o.kind[0].upper()} ")
                else:
                    f.write(f"{tilemap[y][x][0].upper()} ")
            f.write("\n")