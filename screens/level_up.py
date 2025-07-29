import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.metrics import dp
from unit_data import Unit
from tile_effects import (
    get_militia_tile_map,
    get_archer_tile_map,
    get_acolyte_tile_map,
    get_scout_tile_map
)


class LevelUpScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.unit = None  # The selected unit will be passed in later
        self.layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        self.add_widget(self.layout)

        self.tile_map = {}  # Stores effects for this unit’s grid
        self.selected_pos = None  # Used for previewing a tile

    def on_pre_enter(self):
        """Called just before screen is shown. Rebuild layout."""
        self.layout.clear_widgets()

        if self.unit:
            self.build_ui()

    def set_unit(self, unit):
        """Receive a unit object and set up the tile map."""
        self.unit = unit

        # Choose tile map based on unit type
        unit_type = unit.unit_type.lower()

        if unit_type == "militia":
            self.tile_map = get_militia_tile_map()
        elif unit_type == "archer":
            self.tile_map = get_archer_tile_map()
        elif unit_type == "acolyte":
            self.tile_map = get_acolyte_tile_map()
        elif unit_type == "scout":
            self.tile_map = get_scout_tile_map()
        else:
            self.tile_map = {}  # fallback


    def build_ui(self):
        self.layout.clear_widgets()

        # Unit Name & Info
        self.layout.add_widget(Label(text=f"[b]{self.unit.name}[/b] - Choose a new tile to unlock", markup=True, font_size='20sp'))

        # Evolution Grid
        grid = GridLayout(rows=5, cols=5, spacing=dp(4), size_hint_y=None, height=dp(250))

        for row in range(5):
            for col in range(5):
                pos = (row, col)
                is_unlocked = pos in self.unit.unlocked_tiles
                is_adjacent = self._is_adjacent(pos)
                tile_effect = self.tile_map.get(pos, None)

                if is_unlocked:
                    btn = Button(text="✔", background_color=[0.3, 0.8, 0.3, 1], disabled=True)

                elif is_adjacent and tile_effect:
                    btn = Button(
                        text=tile_effect.label,
                        background_color=[0.6, 0.6, 1, 1],
                        font_size='12sp'
                    )
                    btn.bind(on_release=lambda instance, p=pos: self.preview_tile(p))

                else:
                    btn = Button(text="", background_color=[0.5, 0.5, 0.5, 1], disabled=True)

                grid.add_widget(btn)

        self.layout.add_widget(grid)        

        # Add tile preview label
        self.preview_label = Label(text="", font_size='14sp', size_hint_y=None, height=dp(60))
        self.layout.add_widget(self.preview_label)

        # Cancel Button
        cancel = Button(text="Cancel", size_hint_y=None, height=dp(40))
        cancel.bind(on_release=self.go_back)

    def go_back(self, instance):
        self.manager.current = 'units'

        #self.layout.add_widget(cancel)

    def _is_adjacent(self, pos):
        """Check if pos is orthogonally adjacent to any unlocked tile."""
        for tile in self.unit.unlocked_tiles:
            r, c = tile
            pr, pc = pos
            if (abs(r - pr) == 1 and c == pc) or (abs(c - pc) == 1 and r == pr):
                return True
        return False

    def unlock_tile(self, pos):
        """Unlock the tile and return to unit screen."""
        self.unit.unlock_tile(pos)
        self.manager.current = 'units'

    def preview_tile(self, pos):
        """Show the effect of a tile and let player confirm unlock."""
        tile_effect = self.tile_map.get(pos)
        if not tile_effect:
            return

        # Show label + description
        self.preview_label.text = f"[b]{tile_effect.label}[/b]: {tile_effect.flavor_text}"
        self.preview_label.markup = True

        # Show a confirmation button
        confirm_btn = Button(text=f"Unlock '{tile_effect.label}'", size_hint_y=None, height=dp(40))
        confirm_btn.bind(on_release=lambda instance: self.confirm_unlock(pos))
        self.layout.add_widget(confirm_btn)

    def confirm_unlock(self, pos):
        """Apply the effect and unlock the tile."""
        tile_effect = self.tile_map.get(pos)
        if not tile_effect:
            return

        # Unlock tile
        self.unit.unlock_tile(pos)

        # Apply its reward to the unit
        self.unit.apply_tile_effect(tile_effect)

        # Return to unit screen
        self.manager.current = 'units'
