# game_state.py
# Global game state management

class GameState:
    def __init__(self):
        self.selected_units = []  # Units selected for battle
        self.max_party_size = 4   # Maximum units that can be selected
        self.current_level = 1    # Current battle level
        self.game_mode = "campaign"  # campaign, skirmish, etc.
        
    def add_unit_to_party(self, unit):
        """Add a unit to the battle party if there's room."""
        if len(self.selected_units) < self.max_party_size and unit not in self.selected_units:
            self.selected_units.append(unit)
            return True
        return False
    
    def remove_unit_from_party(self, unit):
        """Remove a unit from the battle party."""
        if unit in self.selected_units:
            self.selected_units.remove(unit)
            return True
        return False
    
    def clear_party(self):
        """Clear all units from the battle party."""
        self.selected_units.clear()
    
    def get_party_size(self):
        """Get the current party size."""
        return len(self.selected_units)
    
    def is_unit_selected(self, unit):
        """Check if a unit is selected for battle."""
        return unit in self.selected_units
    
    def can_add_unit(self):
        """Check if more units can be added to the party."""
        return len(self.selected_units) < self.max_party_size

# Global game state instance
game_state = GameState() 