import json
from entities import Star, Planet, SolarSystem

def load_solar_system(filename: str) -> SolarSystem:
    star_system_data = []
    planets_data = []
    
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
        star_system_data = data['star_system']
        stars = []
        if 'primary' in star_system_data:
            stars.append(Star(**star_system_data['primary']))
            stars.append(Star(**star_system_data['secondary']))
        else:
            stars.append(Star(**star_system_data))
        
        planets_data = data['planets']
        planets_data = [Planet(**planet) for planet in planets_data]
    
    return SolarSystem(stars, planets_data)


def get_current_solar_system() -> SolarSystem:
    # For now, just load a hardcoded solar system from a JSON file
    return load_solar_system('non_hm/TEXT_BASED_EXPERIMENT/data/solar_system.json')

