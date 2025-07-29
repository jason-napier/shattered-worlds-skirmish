import sys, os
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.metrics import dp
from kivy.utils import platform
from functools import partial  # Helps pass arguments to button functions

# Allow parent folder import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from unit_data import create_mock_roster, save_army, load_army
from game_state import game_state

class UnitsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Mobile-optimized layout
        padding = dp(15) if platform in ['android', 'ios'] else dp(10)
        spacing = dp(12) if platform in ['android', 'ios'] else dp(10)
        
        # Main screen layout
        self.layout = BoxLayout(orientation='vertical', padding=padding, spacing=spacing)

        # Title and party info
        title_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(80) if platform in ['android', 'ios'] else dp(60)
        )
        
        title_label = Label(
            text="👥 Your Units", 
            font_size='24sp' if platform in ['android', 'ios'] else '20sp',
            size_hint_y=None,
            height=dp(40) if platform in ['android', 'ios'] else dp(30),
            color=(0.9, 0.9, 0.9, 1)
        )
        
        party_info_label = Label(
            text=f"Party: {game_state.get_party_size()}/{game_state.max_party_size}",
            font_size='16sp' if platform in ['android', 'ios'] else '14sp',
            size_hint_y=None,
            height=dp(30) if platform in ['android', 'ios'] else dp(25),
            color=(0.8, 0.8, 0.8, 1)
        )
        
        title_container.add_widget(title_label)
        title_container.add_widget(party_info_label)
        self.layout.add_widget(title_container)
        
        # Store reference to party info label for updates
        self.party_info_label = party_info_label

        # Scrollable area for unit cards
        self.scroll = ScrollView(size_hint=(1, 0.8))

        # Grid inside the scroll for unit entries
        self.unit_grid = GridLayout(cols=1, spacing=spacing, size_hint_y=None)
        self.unit_grid.bind(minimum_height=self.unit_grid.setter('height'))

        # Load saved army or mock unit data
        loaded_army, _ = load_army()
        if loaded_army:
            self.unit_roster = loaded_army
        else:
            self.unit_roster = create_mock_roster()

        # Build UI
        self.refresh_unit_display()

        self.scroll.add_widget(self.unit_grid)
        self.layout.add_widget(self.scroll)

        # Button container
        button_height = dp(60) if platform in ['android', 'ios'] else dp(50)
        button_font = '20sp' if platform in ['android', 'ios'] else '18sp'
        button_container = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=button_height,
            spacing=dp(10)
        )
        
        # Save Army button
        save_button = Button(
            text="💾 Save Army",
            size_hint_x=0.5,
            font_size=button_font
        )
        save_button.bind(on_release=self.save_current_army)
        button_container.add_widget(save_button)

        # Load Army button
        load_button = Button(
            text="📂 Load Army",
            size_hint_x=0.5,
            font_size=button_font
        )
        load_button.bind(on_release=self.load_saved_army)
        button_container.add_widget(load_button)

        # Clear Party button
        clear_button = Button(
            text="🗑️ Clear Party",
            size_hint_x=0.5,
            font_size=button_font
        )
        clear_button.bind(on_release=self.clear_party)
        button_container.add_widget(clear_button)

        # Back to Village button
        back_button = Button(
            text="🏠 Back to Village", 
            size_hint_x=0.5,
            font_size=button_font
        )
        back_button.bind(on_release=self.go_back)
        button_container.add_widget(back_button)

        self.layout.add_widget(button_container)
        self.add_widget(self.layout)

    def refresh_unit_display(self):
        """Rebuilds the unit display grid (used after XP changes)."""
        self.unit_grid.clear_widgets()

        # Rebuild each unit card
        for unit in self.unit_roster:
            unit_card = self.build_unit_card(unit)
            self.unit_grid.add_widget(unit_card)

    def build_unit_card(self, unit):
        """Creates a unit info card with selection and +XP buttons."""
        # Mobile-optimized card dimensions
        card_height = dp(280) if platform in ['android', 'ios'] else dp(240)
        card_padding = dp(12) if platform in ['android', 'ios'] else dp(10)
        card_spacing = dp(8) if platform in ['android', 'ios'] else dp(5)
        
        # Main vertical layout for unit info
        box = BoxLayout(
            orientation='vertical', 
            size_hint_y=None, 
            height=card_height, 
            padding=card_padding, 
            spacing=card_spacing
        )
        stats = unit.get_stats()

        # Mobile-optimized fonts
        title_font = '22sp' if platform in ['android', 'ios'] else '20sp'
        body_font = '18sp' if platform in ['android', 'ios'] else '16sp'
        button_font = '16sp' if platform in ['android', 'ios'] else '14sp'

        # Top: Name and type
        box.add_widget(Label(
            text=f"[b]{unit.name}[/b] ({unit.unit_type})", 
            markup=True, 
            font_size=title_font,
            color=(1, 1, 1, 1)
        ))

        # Level and XP
        level_label = Label(
            text=f"Level {stats['LVL']} | XP: {stats['XP']} / {unit.xp_to_next_level()}",
            font_size=body_font,
            color=(0.9, 0.9, 0.9, 1)
        )
        box.add_widget(level_label)

        # Core stats
        box.add_widget(Label(
            text=f"HP: {stats['HP']}  |  ATK: {stats['ATK']}  |  DEF: {stats['DEF']}", 
            font_size=body_font,
            color=(0.8, 0.8, 0.8, 1)
        ))
        box.add_widget(Label(
            text=f"MOV: {stats['MOV']}  |  RNG: {stats['RNG']}", 
            font_size=body_font,
            color=(0.8, 0.8, 0.8, 1)
        ))

        # Mobile-optimized buttons
        button_height = dp(45) if platform in ['android', 'ios'] else dp(40)
        
        # Selection Button
        is_selected = game_state.is_unit_selected(unit)
        if is_selected:
            select_text = "❌ Remove from Party"
            select_color = (0.8, 0.2, 0.2, 1)
        else:
            if game_state.can_add_unit():
                select_text = "✅ Add to Party"
                select_color = (0.2, 0.8, 0.2, 1)
            else:
                select_text = "🚫 Party Full"
                select_color = (0.5, 0.5, 0.5, 1)
        
        select_button = Button(
            text=select_text,
            size_hint_y=None,
            height=button_height,
            font_size=button_font
        )
        select_button.bind(on_release=partial(self.toggle_unit_selection, unit, select_button))
        box.add_widget(select_button)

        # Add XP Button
        xp_button = Button(
            text="➕ Add 50 XP", 
            size_hint_y=None, 
            height=button_height,
            font_size=button_font
        )
        # Use partial to pass both the unit and label to the method
        xp_button.bind(on_release=partial(self.add_xp_to_unit, unit, level_label))
        box.add_widget(xp_button)

        # Level Up Button (only if there's a tile to unlock)
        if self.unit_has_unspent_level(unit):
            level_up_button = Button(
                text="⭐ Level Up!", 
                size_hint_y=None, 
                height=button_height, 
                font_size=button_font
            )
            level_up_button.bind(on_release=partial(self.go_to_level_up, unit))
            box.add_widget(level_up_button)

        return box

    def add_xp_to_unit(self, unit, level_label, instance):
        """Adds XP to a unit and updates the UI."""
        unit.add_xp(50)  # You can change this value as needed

        # Update the level/XP label in-place
        level_label.text = f"Level {unit.level} | XP: {unit.xp} / {unit.xp_to_next_level()}"

        # Optional: print to console
        print(f"{unit.name} is now level {unit.level} with {unit.xp} XP")

    def go_back(self, instance):
        """Return to the landing screen."""
        self.manager.current = 'landing'

    def unit_has_unspent_level(self, unit):
        # For now, we assume 1 tile unlocked per level
        return unit.level > len(unit.unlocked_tiles)

    def go_to_level_up(self, unit, instance):
        """Send selected unit to LevelUpScreen."""
        self.manager.get_screen('level_up').set_unit(unit)
        self.manager.current = 'level_up'
    
    def toggle_unit_selection(self, unit, button, instance):
        """Toggle unit selection for battle party."""
        if game_state.is_unit_selected(unit):
            # Remove from party
            game_state.remove_unit_from_party(unit)
            button.text = "✅ Add to Party"
        else:
            # Add to party if there's room
            if game_state.add_unit_to_party(unit):
                button.text = "❌ Remove from Party"
        
        # Update party info
        self.party_info_label.text = f"Party: {game_state.get_party_size()}/{game_state.max_party_size}"
        
        # Refresh all unit cards to update selection states
        self.refresh_unit_display()
    
    def clear_party(self, instance):
        """Clear all units from the battle party."""
        game_state.clear_party()
        self.party_info_label.text = f"Party: {game_state.get_party_size()}/{game_state.max_party_size}"
        self.refresh_unit_display()

    def save_current_army(self, instance):
        save_army(self.unit_roster)
        print("Army saved!")

    def load_saved_army(self, instance):
        loaded_army, _ = load_army()
        if loaded_army:
            self.unit_roster = loaded_army
            self.refresh_unit_display()
            print("Army loaded!")
        else:
            print("No saved army found.")
        self.unit_roster = loaded_army if loaded_army else self.unit_roster
