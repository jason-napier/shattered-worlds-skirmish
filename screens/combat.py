from kivy.uix.screenmanager import Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.stacklayout import StackLayout
from kivy.clock import Clock
from kivy.utils import platform
from kivy.core.window import Window
from kivy.uix.popup import Popup
import random

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from unit_data import Unit, load_army, create_mock_roster
from game_state import game_state

# --- Dice System ---
class Die:
    def __init__(self, faces=None):
        # Default: balanced die
        if faces is None:
            faces = ['Sword', 'Sword', 'Shield', 'Shield', 'Pulse', 'Pulse']
        self.faces = faces
        self.sides = len(faces)
    def roll(self):
        return random.choice(self.faces)

def roll_dice(num, unit=None):
    """Roll dice for a unit using their specific die faces."""
    if unit and hasattr(unit, 'die_faces'):
        die = Die(unit.die_faces)
    else:
        die = Die()  # Default balanced die
    return [die.roll() for _ in range(num)]

class CombatScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.upgrades = self.load_upgrades()  # Ensure upgrades is always defined first
        self.grid_size = 5
        
        # Initialize player units from game state
        self.player_units = []
        self.player_positions = {}
        self.enemy_units = []
        self.enemy_positions = {}
        
        # Load selected units from game state
        self.load_player_units()
        
        # Create some enemy units for testing
        self.create_enemy_units()

        self.selected = None
        self.move_tiles = set()  # Valid tiles the player can move to
        self.attack_tiles = set()  # Tiles the selected unit can attack
        self.current_turn = "player"
        self.active_side = "player"  # Alternates between 'player' and 'enemy'
        self.round_number = 1
        self.activated_player_units = set()
        self.activated_enemy_units = set()
        self.passed_last = None  # Track if last action was a pass
        self.activation_phase = None  # 'move' or 'action'
        self.unit_being_activated = None
        self.info_popup = None
        self.player_pulse = 0
        self.enemy_pulse = 0
        self.extra_activation_available = False
        self.reactivate_mode = False

        # Mobile-optimized layout
        padding = dp(15) if platform in ['android', 'ios'] else dp(10)
        spacing = dp(8) if platform in ['android', 'ios'] else dp(10)

        # Main layout
        self.layout = BoxLayout(orientation='vertical', padding=padding, spacing=spacing)
        
        # Add round/turn label
        self.round_label = Label(text=f"Round {self.round_number}", size_hint_y=None, height=dp(30), font_size='16sp')
        self.layout.add_widget(self.round_label)

        # Add pulse display
        self.pulse_label = Label(text=self.get_pulse_text(), size_hint_y=None, height=dp(30), font_size='16sp')
        self.layout.add_widget(self.pulse_label)

        # Mobile-optimized grid spacing
        grid_spacing = dp(3) if platform in ['android', 'ios'] else dp(2)
        self.grid = GridLayout(cols=self.grid_size, spacing=grid_spacing, size_hint_y=0.7)
        
        # Create Turn Label with mobile optimization
        turn_height = dp(40) if platform in ['android', 'ios'] else dp(30)
        turn_font = '20sp' if platform in ['android', 'ios'] else '16sp'
        self.turn_label = Label(
            text="Player Turn", 
            size_hint_y=None, 
            height=turn_height, 
            font_size=turn_font
        )
        self.layout.add_widget(self.turn_label)

        # Mobile-optimized info label
        info_height = dp(60) if platform in ['android', 'ios'] else dp(40)
        info_font = '18sp' if platform in ['android', 'ios'] else '14sp'
        self.info_label = Label(
            text="Select your unit", 
            size_hint_y=None,
            height=info_height,
            font_size=info_font,
            color=(1, 1, 1, 1)
        )
        
        # Mobile-optimized buttons
        button_height = dp(50) if platform in ['android', 'ios'] else dp(40)
        button_font = '18sp' if platform in ['android', 'ios'] else '16sp'
        
        # Button container for better layout
        button_container = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=button_height,
            spacing=dp(5)
        )
        
        # End Turn Button (now always available)
        self.end_turn_btn = Button(
            text="End Turn", 
            size_hint_x=0.33,
            font_size='18sp'
        )
        self.end_turn_btn.bind(on_release=self.end_player_turn)
        button_container.add_widget(self.end_turn_btn)

        # Clear Log Button
        clear_log_button = Button(
            text="Clear Log", 
            size_hint_x=0.33,
            font_size=button_font
        )
        clear_log_button.bind(on_release=lambda instance: self.combat_log_stack.clear_widgets())
        button_container.add_widget(clear_log_button)
        
        # Return to Village Button
        return_button = Button(
            text="🏠 Return", 
            size_hint_x=0.33,
            font_size=button_font
        )
        return_button.bind(on_release=self.return_to_village)
        button_container.add_widget(return_button)
        
        self.layout.add_widget(button_container)

        self.layout.add_widget(self.grid)
        self.layout.add_widget(self.info_label)
        
        # Add a placeholder for phase buttons (will be populated by add_phase_buttons)
        self.phase_button_placeholder = BoxLayout(size_hint_y=None, height=dp(50))
        self.layout.add_widget(self.phase_button_placeholder)

        # Add combat log container with mobile optimization
        log_height = dp(120) if platform in ['android', 'ios'] else dp(100)
        self.combat_log_container = ScrollView(
            size_hint_y=None,
            height=log_height
        )
        self.combat_log_stack = BoxLayout(
            orientation='vertical', 
            size_hint_y=None, 
            spacing=dp(2), 
            padding=dp(4)
        )
        self.combat_log_stack.bind(minimum_height=self.combat_log_stack.setter('height'))
        self.combat_log_container.add_widget(self.combat_log_stack)
        self.layout.add_widget(self.combat_log_container)  

        self.add_widget(self.layout)
        self.build_grid()
        
    def on_enter(self):
        # Always load the saved army and upgrades for battle
        loaded_army, upgrades = load_army()
        self.upgrades = upgrades if upgrades is not None else {}
        if loaded_army:
            game_state.selected_units = loaded_army[:game_state.max_party_size]
        else:
            game_state.selected_units = create_mock_roster()[:game_state.max_party_size]
        self.refresh_combat_setup()
        # Ensure the grid is rebuilt to show buttons
        self.build_grid()
    
    def refresh_combat_setup(self):
        """Refresh the combat setup with current selected units."""
        # Clear existing units
        self.player_units = []
        self.player_positions = {}
        self.enemy_units = []
        self.enemy_positions = {}
        
        # Load current selected units
        self.load_player_units()
        
        # Create new enemy units
        self.create_enemy_units()
        
        # Reset turn state
        self.current_turn = "player"
        self.turn_label.text = "Player Turn"
        self.info_label.text = "Select your unit"
        self.round_number = 1
        self.activated_player_units = set()
        self.activated_enemy_units = set()
        self.passed_last = None
        self.active_side = "player"
        self.activation_phase = None
        self.unit_being_activated = None
        self.player_pulse = 0
        self.enemy_pulse = 0
        self.round_label.text = f"Round {self.round_number}"
        self.update_pulse_display()
        
        # Clear selection and tiles
        self.selected = None
        self.move_tiles.clear()
        self.attack_tiles.clear()
        
        # Rebuild the grid
        self.build_grid()
    
    def load_player_units(self):
        """Load selected units from game state and assign positions."""
        selected_units = game_state.selected_units
        
        if not selected_units:
            # If no units selected, create a default unit
            default_unit = Unit("Militia 1", "Militia")
            default_unit2 = Unit("Militia 2", "Militia")
            self.player_units = [default_unit,default_unit2]
            self.player_positions[default_unit] = (4, 2)
            self.player_positions[default_unit2] = (3, 2)
        else:
            self.player_units = selected_units.copy()
            # Assign positions to player units (bottom of grid)
            positions = [(4, 1), (4, 2), (4, 3), (3, 2)]  # Bottom row and one above
            for i, unit in enumerate(self.player_units):
                if i < len(positions):
                    self.player_positions[unit] = positions[i]
                else:
                    # If more units than positions, place them randomly
                    import random
                    while True:
                        pos = (random.randint(3, 4), random.randint(0, 4))
                        if pos not in self.player_positions.values():
                            self.player_positions[unit] = pos
                            break
        
        # Reset HP for all player units
        for unit in self.player_units:
            unit.current_hp = unit.hp
    
    def create_enemy_units(self):
        """Create enemy units for the battle."""
        # Create enemy units based on party size
        num_enemies = min(len(self.player_units) + 1, 3)  # 1-3 enemies
        
        enemy_types = ["Warrior", "Runeguard", "Arcane Archer"]
        for i in range(num_enemies):
            enemy = Unit(f"Enemy {enemy_types[i % len(enemy_types)]} {i+1}", enemy_types[i % len(enemy_types)])
            self.enemy_units.append(enemy)
            # Place enemies at top of grid
            self.enemy_positions[enemy] = (0, i + 1)
    
    def get_unit_at_position(self, pos):
        """Get the unit at a given position."""
        # Check player units
        for unit, unit_pos in self.player_positions.items():
            if unit_pos == pos and unit.is_alive():
                return unit, "player"
        
        # Check enemy units
        for unit, unit_pos in self.enemy_positions.items():
            if unit_pos == pos and unit.is_alive():
                return unit, "enemy"
        
        return None, None

    def build_grid(self):
        self.grid.clear_widgets()
        tile_font = '16sp' if platform in ['android', 'ios'] else '14sp'
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                pos = (row, col)
                text = ""
                color = [0.7, 0.7, 0.7, 1]
                unit, unit_type = self.get_unit_at_position(pos)
                if unit:
                    if unit_type == "player":
                        text = f"{unit.name}\n{unit.current_hp} HP"
                        if unit in self.activated_player_units:
                            color = [0.5, 0.5, 0.5, 1]
                        else:
                            color = [0.3, 0.8, 0.3, 1]
                        if self.selected == pos:
                            color = [0.2, 0.9, 0.2, 1]
                    else:
                        text = f"{unit.name}\n{unit.current_hp} HP"
                        if unit in self.activated_enemy_units:
                            color = [0.7, 0.3, 0.3, 1]
                        else:
                            color = [0.9, 0.3, 0.3, 1]
                if pos in self.move_tiles:
                    color = [0.4, 0.6, 1, 1]
                if pos in self.attack_tiles:
                    # Show heal tiles in green for Clerics, red for others
                    if self.unit_being_activated and self.unit_being_activated.unit_type == "Cleric":
                        color = [0.4, 1, 0.4, 1]  # Green for healing
                    else:
                        color = [1, 0.4, 0.4, 1]  # Red for attacking
                btn = Button(
                    text=text, 
                    background_color=color, 
                    font_size=tile_font,
                    size_hint=(1, 1)
                )
                btn.bind(on_release=lambda instance, p=pos: self.on_tile_clicked(p))
                self.grid.add_widget(btn)
        self.add_phase_buttons()
        self.add_info_button()
        self.add_special_ability_buttons()

    def add_info_button(self):
        # Remove old info button container if any
        if hasattr(self, 'info_button_container') and self.info_button_container:
            if self.info_button_container.parent:
                self.layout.remove_widget(self.info_button_container)
        self.info_button_container = None
        # Show Info/Cancel buttons if a unit is selected for info (not in move/action phase)
        if self.selected and self.activation_phase is None:
            unit, unit_type = self.get_unit_at_position(self.selected)
            if unit and (
                (unit_type == "player" and unit not in self.activated_player_units)
                or unit_type == "enemy"
            ):
                container = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
                info_btn = Button(text="Info", font_size='16sp')
                info_btn.bind(on_release=lambda instance: self.show_unit_info(unit))
                cancel_btn = Button(text="Cancel", font_size='16sp')
                cancel_btn.bind(on_release=self.cancel_activation)
                container.add_widget(info_btn)
                container.add_widget(cancel_btn)
                self.layout.add_widget(container)
                self.info_button_container = container

    def add_special_ability_buttons(self):
        # Remove old ability button container if any
        if hasattr(self, 'ability_button_container') and self.ability_button_container:
            if self.ability_button_container.parent:
                self.layout.remove_widget(self.ability_button_container)
        self.ability_button_container = None
        # Only show if Wizard's Tower is unlocked
        if self.upgrades.get('wizards_tower'):
            container = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
            # Activate Another Unit
            activate_btn = Button(text="Activate Another Unit (10 Pulse)", font_size='16sp', disabled=self.player_pulse < 2 or self.extra_activation_available)
            activate_btn.bind(on_release=self.activate_another_unit)
            # Reactivate Unit
            reactivate_btn = Button(text="Reactivate Unit (10 Pulse)", font_size='16sp', disabled=self.player_pulse < 2 or self.reactivate_mode)
            reactivate_btn.bind(on_release=self.start_reactivate_mode)
            container.add_widget(activate_btn)
            container.add_widget(reactivate_btn)
            self.layout.add_widget(container)
            self.ability_button_container = container

    def on_tile_clicked(self, pos):
        acted = False
        if self.reactivate_mode:
            unit, unit_type = self.get_unit_at_position(pos)
            if unit_type == "player" and unit in self.activated_player_units:
                self.activated_player_units.remove(unit)
                self.info_label.text = f"{unit.name} is reactivated and can act again!"
                self.reactivate_mode = False
                self.build_grid()
            return
        if self.active_side != "player":
            return
        unit, unit_type = self.get_unit_at_position(pos)
        if self.activation_phase is None:
            # Start activation: select unit
            if unit_type == "player" and unit not in self.activated_player_units:
                self.selected = pos
                self.unit_being_activated = unit
                self.activation_phase = 'move'
                self.move_tiles = self.get_move_tiles(pos, unit.mov)
                self.attack_tiles.clear()
                self.info_label.text = f"{unit.name}: Move phase. Tap a blue tile to move or press Stay."
                self.build_grid()
                return
            elif unit_type == "enemy":
                self.selected = pos
                self.unit_being_activated = None
                self.move_tiles.clear()
                self.attack_tiles.clear()
                self.info_label.text = f"{unit.name}: Enemy info. Press Info to view stats, or Cancel."
                self.build_grid()
                return
        elif self.activation_phase == 'move':
            if pos in self.move_tiles:
                # Check if the target position is occupied by a friendly unit
                unit_at_pos, unit_type = self.get_unit_at_position(pos)
                if unit_at_pos and unit_type == "player":
                    # Find an empty tile nearby to end movement
                    final_pos = self.find_empty_tile_near(pos)
                    if final_pos:
                        self.player_positions[self.unit_being_activated] = final_pos
                        self.info_label.text = f"{self.unit_being_activated.name} moved through friendly unit to {final_pos}. Now choose an action."
                    else:
                        # No empty tile found, stay in place
                        self.info_label.text = f"{self.unit_being_activated.name} cannot find space to end movement. Staying in place."
                        final_pos = self.player_positions[self.unit_being_activated]
                else:
                    # Empty tile or enemy tile, move there
                    self.player_positions[self.unit_being_activated] = pos
                    self.info_label.text = f"{self.unit_being_activated.name} moved. Now choose an action."
                    final_pos = pos
                
                self.activation_phase = 'action'
                self.move_tiles.clear()
                # Clerics can target friendly units, others target enemies
                if self.unit_being_activated.unit_type == "Cleric":
                    self.attack_tiles = self.get_heal_tiles(final_pos, self.unit_being_activated.rng)
                else:
                    self.attack_tiles = self.get_attack_tiles(final_pos, self.unit_being_activated.rng)
                self.build_grid()
        elif self.activation_phase == 'action':
            target_unit, target_type = self.get_unit_at_position(pos)
            
            # Handle Cleric special case - they can't attack enemies
            if self.unit_being_activated.unit_type == "Cleric":
                if target_type == "player" and target_unit.is_alive() and pos in self.attack_tiles:
                    # Cleric healing/buffing action
                    self.handle_cleric_action(target_unit)
                else:
                    self.info_label.text = f"{self.unit_being_activated.name} can only target friendly units for healing/buffing."
                    return
            elif target_type == "enemy" and target_unit.is_alive() and pos in self.attack_tiles:
                # --- Dice-based combat for non-Cleric units ---
                atk_dice = roll_dice(self.unit_being_activated.atk, self.unit_being_activated)
                def_dice = roll_dice(target_unit.def_, target_unit)
                swords = atk_dice.count('Sword')
                shields = def_dice.count('Shield')
                pulse_att = atk_dice.count('Pulse')
                pulse_def = def_dice.count('Pulse')
                net_damage = max(0, swords - shields)
                # Update Pulse pools
                self.player_pulse += pulse_att
                self.enemy_pulse += pulse_def
                self.update_pulse_display()
                # Apply damage
                target_unit.current_hp -= net_damage
                # Log dice results
                self.log(f"{self.unit_being_activated.name} rolled: {atk_dice}")
                self.log(f"{target_unit.name} rolled: {def_dice}")
                self.log(f"Swords: {swords}, Shields: {shields}, Player Pulse: +{pulse_att}, Enemy Pulse: +{pulse_def}")
                self.info_label.text = f"{self.unit_being_activated.name} attacked {target_unit.name}! {net_damage} damage dealt."
                if net_damage > 0:
                    self.log(f"{self.unit_being_activated.name} dealt {net_damage} damage to {target_unit.name}.")
                else:
                    self.log(f"{target_unit.name} blocked all damage!")
                if target_unit.current_hp <= 0:
                    self.info_label.text += " Enemy defeated!"
                    self.log(f"{target_unit.name} was defeated!")
                    self.enemy_positions.pop(target_unit, None)
                
                # Complete activation
                self.complete_unit_activation()

    def stay_in_place(self, instance):
        # Called when player chooses to stay instead of moving
        if self.activation_phase == 'move' and self.unit_being_activated:
            pos = self.player_positions[self.unit_being_activated]
            self.info_label.text = f"{self.unit_being_activated.name} stayed in place. Now choose an action."
            self.activation_phase = 'action'
            self.move_tiles.clear()
            # Clerics can target friendly units, others target enemies
            if self.unit_being_activated.unit_type == "Cleric":
                self.attack_tiles = self.get_heal_tiles(pos, self.unit_being_activated.rng)
            else:
                self.attack_tiles = self.get_attack_tiles(pos, self.unit_being_activated.rng)
            self.build_grid()

    def pass_action_phase(self, instance):
        # Called when player chooses to pass their action
        if self.activation_phase == 'action' and self.unit_being_activated:
            self.activated_player_units.add(self.unit_being_activated)
            self.selected = None
            self.unit_being_activated = None
            self.activation_phase = None
            self.move_tiles.clear()
            self.attack_tiles.clear()
            self.build_grid()
            self.pass_activation()

    def _is_adjacent(self, a, b):
        """Check if tile b is orthogonally adjacent to tile a."""
        ax, ay = a
        bx, by = b
        return (abs(ax - bx) == 1 and ay == by) or (abs(ay - by) == 1 and ax == bx)
    
    def get_move_tiles(self, start_pos, max_range):
        """Return all reachable tiles from start_pos within movement range."""
        reachable = set()
        queue = [(start_pos, 0)]

        while queue:
            (x, y), dist = queue.pop(0)
            if dist > max_range or (x, y) in reachable:
                continue

            # Check if tile is occupied by an enemy unit
            unit, unit_type = self.get_unit_at_position((x, y))
            if unit and unit_type == "enemy" and (x, y) != start_pos:
                continue

            reachable.add((x, y))

            # Explore neighbors (orthogonal)
            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                    queue.append(((nx, ny), dist + 1))

        # Remove starting tile
        reachable.discard(start_pos)
        return reachable
    
    def get_attack_tiles(self, start_pos, rng):
        """Return tiles in attack range from a given position."""
        x0, y0 = start_pos
        attackable = set()

        for dx in range(-rng, rng + 1):
            for dy in range(-rng, rng + 1):
                dist = abs(dx) + abs(dy)
                if 0 < dist <= rng:
                    x, y = x0 + dx, y0 + dy
                    if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
                        attackable.add((x, y))

        return attackable
    
    def get_heal_tiles(self, start_pos, rng):
        """Return tiles in healing range from a given position (friendly units only)."""
        x0, y0 = start_pos
        healable = set()

        for dx in range(-rng, rng + 1):
            for dy in range(-rng, rng + 1):
                dist = abs(dx) + abs(dy)
                if 0 < dist <= rng:
                    x, y = x0 + dx, y0 + dy
                    if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
                        # Check if there's a friendly unit at this position
                        unit, unit_type = self.get_unit_at_position((x, y))
                        if unit and unit_type == "player":
                            healable.add((x, y))

        return healable
    
    def find_empty_tile_near(self, target_pos, max_distance=3):
        """Find an empty tile near the target position for units to end their movement."""
        x0, y0 = target_pos
        
        # Check the target position first
        unit, _ = self.get_unit_at_position(target_pos)
        if not unit:
            return target_pos
            
        # Search in expanding circles
        for distance in range(1, max_distance + 1):
            for dx in range(-distance, distance + 1):
                for dy in range(-distance, distance + 1):
                    if abs(dx) + abs(dy) == distance:  # Manhattan distance
                        x, y = x0 + dx, y0 + dy
                        if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
                            unit, _ = self.get_unit_at_position((x, y))
                            if not unit:
                                return (x, y)
        
        # If no empty tile found, return None
        return None
    
    def handle_cleric_action(self, target_unit):
        """Handle Cleric's healing/buffing action on a friendly unit."""
        # Roll dice for Cleric's action
        action_dice = roll_dice(self.unit_being_activated.atk, self.unit_being_activated)
        shields = action_dice.count('Shield')
        pulse_gained = action_dice.count('Pulse')
        
        # Clerics use Shields for healing, Pulse for buffing
        healing = shields
        if healing > 0:
            old_hp = target_unit.current_hp
            target_unit.current_hp = min(target_unit.hp, target_unit.current_hp + healing)
            actual_healing = target_unit.current_hp - old_hp
            self.log(f"{self.unit_being_activated.name} rolled: {action_dice}")
            self.log(f"{self.unit_being_activated.name} healed {target_unit.name} for {actual_healing} HP!")
            self.info_label.text = f"{self.unit_being_activated.name} healed {target_unit.name} for {actual_healing} HP!"
        else:
            self.log(f"{self.unit_being_activated.name} rolled: {action_dice}")
            self.log(f"{self.unit_being_activated.name} failed to heal {target_unit.name}.")
            self.info_label.text = f"{self.unit_being_activated.name} failed to heal {target_unit.name}."
        
        # Add Pulse to player pool
        self.player_pulse += pulse_gained
        self.update_pulse_display()
        
        # Complete activation
        self.complete_unit_activation()
    
    def complete_unit_activation(self):
        """Complete the current unit's activation and handle turn transitions."""
        self.activated_player_units.add(self.unit_being_activated)
        self.selected = None
        self.unit_being_activated = None
        self.activation_phase = None
        self.move_tiles.clear()
        self.attack_tiles.clear()
        self.build_grid()
        
        # Handle extra activation
        if self.extra_activation_available:
            self.extra_activation_available = False
            self.info_label.text = "You may activate another unit this turn!"
            self.build_grid()
            return
        
        self.pass_activation()
        
    def log(self, message):
        """Add a message to the top of the combat log."""
        label = Label(text=message, size_hint_y=None, height=dp(20), font_size='14sp', halign='left', valign='middle')
        label.bind(size=label.setter('text_size'))  # Wrap long text
        self.combat_log_stack.add_widget(label, index=0)  # Add at the top

    def pass_activation(self):
        # Called after a side activates a unit or passes
        self.check_battle_end()
        # Check if both sides are done
        player_left = [u for u in self.player_units if u.is_alive() and u not in self.activated_player_units]
        enemy_left = [u for u in self.enemy_units if u.is_alive() and u not in self.activated_enemy_units]
        if not player_left and not enemy_left:
            self.info_label.text = "Both sides finished. New round will begin."
            Clock.schedule_once(self.start_new_round, 1.0)
            return
        # Alternate to the other side if they have unactivated units
        if self.active_side == "player":
            if enemy_left:
                self.active_side = "enemy"
                self.info_label.text = "Enemy's turn."
                Clock.schedule_once(self.enemy_turn, 0.5)
            else:
                # Enemy has no units left, player continues
                self.active_side = "player"
        else:
            if player_left:
                self.active_side = "player"
                self.info_label.text = "Your turn."
            else:
                # Player has no units left, enemy continues
                self.active_side = "enemy"
                Clock.schedule_once(self.enemy_turn, 0.5)

    def end_player_turn(self, instance):
        # Player voluntarily passes (does NOT activate all units)
        self.selected = None
        self.move_tiles.clear()
        self.attack_tiles.clear()
        self.build_grid()
        self.pass_activation()

    def enemy_turn(self, dt):
        # Enemy activates one unactivated unit
        unactivated = [u for u in self.enemy_units if u.is_alive() and u not in self.activated_enemy_units]
        if unactivated:
            enemy = unactivated[0]
            enemy_pos = self.enemy_positions[enemy]
            # Find closest player unit
            closest_player = None
            closest_distance = float('inf')
            for player_unit, player_pos in self.player_positions.items():
                if player_unit.is_alive():
                    distance = abs(enemy_pos[0] - player_pos[0]) + abs(enemy_pos[1] - player_pos[1])
                    if distance < closest_distance:
                        closest_distance = distance
                        closest_player = (player_unit, player_pos)
            if closest_player:
                target_unit, target_pos = closest_player
                # If adjacent, attack
                if closest_distance == 1:
                    # --- Dice-based combat for enemy ---
                    atk_dice = roll_dice(enemy.atk, enemy)
                    def_dice = roll_dice(target_unit.def_, target_unit)
                    swords = atk_dice.count('Sword')
                    shields = def_dice.count('Shield')
                    pulse_att = atk_dice.count('Pulse')
                    pulse_def = def_dice.count('Pulse')
                    net_damage = max(0, swords - shields)
                    # Update Pulse pools
                    self.enemy_pulse += pulse_att
                    self.player_pulse += pulse_def
                    self.update_pulse_display()
                    # Apply damage
                    target_unit.current_hp -= net_damage
                    # Log dice results
                    self.log(f"{enemy.name} rolled: {atk_dice}")
                    self.log(f"{target_unit.name} rolled: {def_dice}")
                    self.log(f"Swords: {swords}, Shields: {shields}, Enemy Pulse: +{pulse_att}, Player Pulse: +{pulse_def}")
                    if net_damage > 0:
                        self.log(f"{enemy.name} dealt {net_damage} damage to {target_unit.name}.")
                    else:
                        self.log(f"{target_unit.name} blocked all damage!")
                    if target_unit.current_hp <= 0:
                        self.log(f"{target_unit.name} has fallen!")
                else:
                    # Move toward closest player
                    ex, ey = enemy_pos
                    px, py = target_pos
                    dx = px - ex
                    dy = py - ey
                    if abs(dx) > abs(dy):
                        step = (ex + (1 if dx > 0 else -1), ey)
                    else:
                        step = (ex, ey + (1 if dy > 0 else -1))
                    if (0 <= step[0] < self.grid_size and 0 <= step[1] < self.grid_size):
                        unit_at_step, unit_type = self.get_unit_at_position(step)
                        if not unit_at_step:
                            # Empty tile, move there
                            self.enemy_positions[enemy] = step
                            self.log(f"{enemy.name} moved to {step}.")
                        elif unit_type == "enemy":
                            # Friendly unit, find empty tile nearby to end movement
                            final_pos = self.find_empty_tile_near(step)
                            if final_pos:
                                self.enemy_positions[enemy] = final_pos
                                self.log(f"{enemy.name} moved through friendly unit to {final_pos}.")
                            # If no empty tile found, enemy stays in place
                        # If enemy unit is blocking, enemy stays in place
            self.activated_enemy_units.add(enemy)
            self.build_grid()
            self.pass_activation()
        else:
            # No unactivated enemy units, just pass
            self.pass_activation()

    def start_new_round(self, dt):
        self.round_number += 1
        self.activated_player_units.clear()
        self.activated_enemy_units.clear()
        self.round_label.text = f"Round {self.round_number}"
        self.info_label.text = f"Round {self.round_number} begins!"
        self.build_grid()
        self.current_turn = "player"
        self.active_side = "player"
        self.selected = None
        self.move_tiles.clear()
        self.attack_tiles.clear()
        self.passed_last = None
        self.update_pulse_display()

    def check_battle_end(self):
        # Check if all enemies are defeated
        alive_enemies = [unit for unit in self.enemy_units if unit.is_alive()]
        if not alive_enemies:
            self.log("🎉 Victory! All enemies defeated!")
            self.info_label.text = "Victory! All enemies defeated!"
            return
        # Check if all player units are defeated
        alive_players = [unit for unit in self.player_units if unit.is_alive()]
        if not alive_players:
            self.log("💀 Defeat! All your units have fallen!")
            self.info_label.text = "Defeat! All your units have fallen!"
            return

    def return_to_village(self, instance):
        """Return to the village (landing screen)."""
        # Always allow returning to the landing screen
        self.selected = None
        self.move_tiles.clear()
        self.attack_tiles.clear()
        self.log("🏠 Returning to village...")
        self.manager.current = 'landing'

    def show_unit_info(self, unit):
        # Show a popup with unit stats and a Cancel button
        stats = unit.get_stats()
        info_text = f"[b]{unit.name}[/b] ({unit.unit_type})\n"
        info_text += f"HP: {unit.current_hp}/{unit.hp}\nATK: {unit.atk}\nDEF: {unit.def_}\nMOV: {unit.mov}\nRNG: {unit.rng}\nLVL: {unit.level}\nXP: {unit.xp}\n"
        info_text += f"Die: {', '.join(unit.die_faces)}"
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        label = Label(text=info_text, markup=True, font_size='18sp', halign='left', valign='top')
        label.bind(size=label.setter('text_size'))
        content.add_widget(label)
        close_btn = Button(text="Close", size_hint_y=None, height=dp(40), font_size='16sp')
        close_btn.bind(on_release=self.dismiss_info_popup)
        content.add_widget(close_btn)
        self.info_popup = Popup(title="Unit Info", content=content, size_hint=(None, None), size=(dp(320), dp(400)), auto_dismiss=False)
        self.info_popup.open()

    def dismiss_info_popup(self, instance):
        if self.info_popup:
            self.info_popup.dismiss()
            self.info_popup = None

    def cancel_activation(self, instance):
        # Cancel the current activation phase, return to selection state
        self.selected = None
        self.unit_being_activated = None
        self.activation_phase = None
        self.move_tiles.clear()
        self.attack_tiles.clear()
        self.build_grid()

    def add_phase_buttons(self):
        # Clear the placeholder
        self.phase_button_placeholder.clear_widgets()
        
        if self.activation_phase == 'move':
            stay_btn = Button(text="Stay", font_size='16sp')
            stay_btn.bind(on_release=self.stay_in_place)
            info_btn = Button(text="Info", font_size='16sp')
            if self.unit_being_activated:
                info_btn.bind(on_release=lambda instance: self.show_unit_info(self.unit_being_activated))
            cancel_btn = Button(text="Cancel", font_size='16sp')
            cancel_btn.bind(on_release=self.cancel_activation)
            self.phase_button_placeholder.add_widget(stay_btn)
            self.phase_button_placeholder.add_widget(info_btn)
            self.phase_button_placeholder.add_widget(cancel_btn)
        elif self.activation_phase == 'action':
            pass_btn = Button(text="Pass", font_size='16sp')
            pass_btn.bind(on_release=self.pass_action_phase)
            info_btn = Button(text="Info", font_size='16sp')
            if self.unit_being_activated:
                info_btn.bind(on_release=lambda instance: self.show_unit_info(self.unit_being_activated))
            cancel_btn = Button(text="Cancel", font_size='16sp')
            cancel_btn.bind(on_release=self.cancel_activation)
            self.phase_button_placeholder.add_widget(pass_btn)
            self.phase_button_placeholder.add_widget(info_btn)
            self.phase_button_placeholder.add_widget(cancel_btn)

    def get_pulse_text(self):
        return f"Player Pulse: {self.player_pulse}    Enemy Pulse: {self.enemy_pulse}"

    def update_pulse_display(self):
        self.pulse_label.text = self.get_pulse_text()

    def load_upgrades(self):
        _, upgrades = load_army()
        return upgrades if upgrades is not None else {}

    def activate_another_unit(self, instance):
        pulse_cost = 10
        if self.player_pulse >= pulse_cost and not self.extra_activation_available:
            self.player_pulse -= pulse_cost
            self.update_pulse_display()
            self.extra_activation_available = True
            self.info_label.text = "You may activate an extra unit this turn!"
            self.build_grid()

    def start_reactivate_mode(self, instance):
        react_cost = 10
        if self.player_pulse >= react_cost and not self.reactivate_mode:
            self.player_pulse -= react_cost
            self.update_pulse_display()
            self.reactivate_mode = True
            self.info_label.text = "Select an already activated unit to reactivate."
            self.build_grid()

