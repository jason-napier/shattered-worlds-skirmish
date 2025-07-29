# unit_data.py

# This class defines the structure for a unit in the game.
# Each unit has a name, type, level, experience, stats, and evolution grid data.

import json
import os

class Unit:
    def __init__(self, name, unit_type):
        # Basic info
        self.name = name                # Display name of the unit
        self.unit_type = unit_type      # Warrior, Runeguard, Arcane Archer, Cleric

        # Leveling and XP
        self.level = 1                  # Starting level
        self.xp = 0                     # Starting XP

        # Unit type definitions with stats and dice
        self.unit_definitions = {
            'Warrior': {
                'hp': 5, 'atk': 3, 'def_': 2, 'mov': 3, 'rng': 1,
                'die_faces': ['Sword', 'Sword', 'Shield', 'Shield', 'Pulse', 'Pulse']
            },
            'Runeguard': {
                'hp': 5, 'atk': 3, 'def_': 3, 'mov': 2, 'rng': 1,
                'die_faces': ['Sword', 'Shield', 'Shield', 'Shield', 'Pulse', 'Pulse']
            },
            'Arcane Archer': {
                'hp': 3, 'atk': 3, 'def_': 2, 'mov': 3, 'rng': 2,
                'die_faces': ['Sword', 'Sword', 'Sword', 'Shield', 'Pulse', 'Pulse']
            },
            'Cleric': {
                'hp': 5, 'atk': 4, 'def_': 2, 'mov': 3, 'rng': 1,
                'die_faces': ['Shield', 'Shield', 'Pulse', 'Pulse', 'Pulse', 'Pulse']
            }
        }

        # Set stats based on unit type
        if unit_type in self.unit_definitions:
            def_stats = self.unit_definitions[unit_type]
            self.hp = def_stats['hp']
            self.atk = def_stats['atk']
            self.def_ = def_stats['def_']
            self.mov = def_stats['mov']
            self.rng = def_stats['rng']
            self.die_faces = def_stats['die_faces']
        else:
            # Fallback for unknown unit types
            self.hp = 5
            self.atk = 3
            self.def_ = 2
            self.mov = 3
            self.rng = 1
            self.die_faces = ['Sword', 'Sword', 'Shield', 'Shield', 'Pulse', 'Pulse']

        # Evolution Grid
        # Grid is 5x5, positions are stored as (row, column), e.g., (2, 2) is center
        self.evolution_position = (2, 2)           # Start at center of grid
        self.unlocked_tiles = {(2, 2)}             # Set of all unlocked tiles (start with center)
        self.available_tiles = set()               # All available tiles based on unit's possition (Not in Chat-GPT)

        self.abilities = []  # List of ability IDs
        self.traits = []     # List of passive trait IDs

        self.current_hp = self.hp  # Track HP during battle

    def add_xp(self, amount):
        """Add XP and level up if threshold is reached."""
        self.xp += amount

        # Simple level-up rule: every 100 XP = +1 level
        while self.xp >= self.xp_to_next_level():
            self.xp -= self.xp_to_next_level()
            self.level += 1

    def xp_to_next_level(self):
        """Returns how much XP is needed for next level."""
        return 100  # For now, a flat requirement per level

    def unlock_tile(self, new_pos):
        """Unlock a new evolution tile if it's adjacent to a current one."""
        if self._is_adjacent(new_pos):
            self.unlocked_tiles.add(new_pos)
            self.evolution_position = new_pos  # Move to the new tile

    def _is_adjacent(self, new_pos):
        """Checks if the new tile is adjacent (orthogonally) to a current unlocked tile."""
        for tile in self.unlocked_tiles:
            r, c = tile
            nr, nc = new_pos
            if (abs(r - nr) == 1 and c == nc) or (abs(c - nc) == 1 and r == nr):
                return True
        return False

    def get_stats(self):
        """Return unit stats as a dictionary (for display)."""
        return {
            "HP": self.hp,
            "ATK": self.atk,
            "DEF": self.def_,
            "MOV": self.mov,
            "RNG": self.rng,
            "LVL": self.level,
            "XP": self.xp
        }
    
    def apply_tile_effect(self, tile_effect):
        """Apply a TileEffect object to this unit."""
        tile_effect.apply_to(self)

    def is_alive(self):
        return self.current_hp > 0

    def to_dict(self):
        return {
            'name': self.name,
            'unit_type': self.unit_type,
            'level': self.level,
            'xp': self.xp,
            'hp': self.hp,
            'atk': self.atk,
            'def_': self.def_,
            'mov': self.mov,
            'rng': self.rng,
            'current_hp': self.current_hp,
            'die_faces': self.die_faces,
            'evolution_position': self.evolution_position,
            'unlocked_tiles': list(self.unlocked_tiles),
            'available_tiles': list(self.available_tiles),
            'abilities': self.abilities,
            'traits': self.traits
        }

    @classmethod
    def from_dict(cls, data):
        unit = cls(data['name'], data['unit_type'])
        unit.level = data.get('level', 1)
        unit.xp = data.get('xp', 0)
        unit.hp = data.get('hp', 10)
        unit.atk = data.get('atk', 3)
        unit.def_ = data.get('def_', 2)
        unit.mov = data.get('mov', 3)
        unit.rng = data.get('rng', 1)
        unit.current_hp = data.get('current_hp', unit.hp)
        unit.die_faces = data.get('die_faces', ['Sword', 'Sword', 'Shield', 'Shield', 'Pulse', 'Pulse'])
        unit.evolution_position = tuple(data.get('evolution_position', (2, 2)))
        unit.unlocked_tiles = set(tuple(t) for t in data.get('unlocked_tiles', [(2, 2)]))
        unit.available_tiles = set(tuple(t) for t in data.get('available_tiles', []))
        unit.abilities = data.get('abilities', [])
        unit.traits = data.get('traits', [])
        return unit

#Create Mock Units Roster
def create_mock_roster():
    """Returns a list of example units to test with."""
    unit1 = Unit("Warrior 1", "Warrior")
    unit2 = Unit("Runeguard 1", "Runeguard")
    unit3 = Unit("Arcane Archer 1", "Arcane Archer")
    unit4 = Unit("Cleric 1", "Cleric")

    # Give some XP to show progression
    unit2.add_xp(180)  # Will be level 2 with 80 XP
    unit1.add_xp(250)  # Will be level 3 with 50 XP

    return [unit1, unit2, unit3, unit4]

def save_army(units, filename='savegame.json', upgrades=None):
    data = {
        'units': [unit.to_dict() for unit in units],
        'upgrades': upgrades if upgrades is not None else {}
    }
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

def load_army(filename='savegame.json'):
    if not os.path.exists(filename):
        return None, {}
    with open(filename, 'r') as f:
        data = json.load(f)
    # If data is a list, it's the old format
    if isinstance(data, list):
        units = [Unit.from_dict(u) for u in data]
        upgrades = {}
    else:
        units = [Unit.from_dict(u) for u in data.get('units', [])]
        upgrades = data.get('upgrades', {})
    return units, upgrades
