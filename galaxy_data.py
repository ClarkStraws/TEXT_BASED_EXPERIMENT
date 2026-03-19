# ----------------------------
# Galaxy map data
# ----------------------------
# Each entry is a star system visible on the galaxy map.
# gx/gy are pixel positions within the galaxy viewport (VIEWPORT_W x VIEWPORT_H).
# Star-8008 uses the actual solar_system.json data; others are display-only for now.

GALAXY_SYSTEMS = [
    {
        "name": "Star-8008",
        "gx": 310,
        "gy": 220,
        "color": (255, 204, 111),
        "classification": "M",
        "data_file": "data/solar_system.json",
        "description": "An M-class red dwarf. Three cold worlds orbit in darkness.",
    },
    {
        "name": "Vega-Prime",
        "gx": 500,
        "gy": 145,
        "color": (200, 215, 255),
        "classification": "A",
        "data_file": None,
        "description": "A brilliant A-class star. High radiation. Proceed with caution.",
    },
    {
        "name": "Cinder-3",
        "gx": 185,
        "gy": 330,
        "color": (255, 150, 70),
        "classification": "K",
        "data_file": None,
        "description": "A K-class orange giant. Rich asteroid fields orbit the outer belt.",
    },
    {
        "name": "Nephele",
        "gx": 560,
        "gy": 370,
        "color": (255, 255, 180),
        "classification": "G",
        "data_file": None,
        "description": "A G-class star like Sol. Unknown planetary bodies detected.",
    },
    {
        "name": "Atrox-9",
        "gx": 140,
        "gy": 130,
        "color": (160, 180, 255),
        "classification": "B",
        "data_file": None,
        "description": "A volatile B-class star. Dense debris fields. Extreme caution advised.",
    },
]

# Fuel cost to jump between any two systems (flat rate for simplicity)
FUEL_PER_JUMP = 20
