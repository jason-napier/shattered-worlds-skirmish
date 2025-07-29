import sys, os
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.metrics import dp
from kivy.utils import platform

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from unit_data import save_army, load_army, create_mock_roster

class StructuresScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))
        self.upgrades = self.load_upgrades()
        self.build_ui()
        self.add_widget(self.layout)

    def build_ui(self):
        self.layout.clear_widgets()
        title = Label(text="🏰 Village Upgrades", font_size='24sp', size_hint_y=None, height=dp(50))
        self.layout.add_widget(title)

        # Wizard's Tower Section
        tower_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60), spacing=dp(10))
        tower_label = Label(text="Wizard's Tower", font_size='20sp', size_hint_x=0.6)
        status = "Unlocked" if self.upgrades.get('wizards_tower') else "Locked"
        status_label = Label(text=f"[b]{status}[/b]", markup=True, font_size='18sp', size_hint_x=0.2)
        tower_box.add_widget(tower_label)
        tower_box.add_widget(status_label)
        if not self.upgrades.get('wizards_tower'):
            unlock_btn = Button(text="Unlock", size_hint_x=0.2, font_size='16sp')
            unlock_btn.bind(on_release=self.unlock_wizards_tower)
            tower_box.add_widget(unlock_btn)
        self.layout.add_widget(tower_box)

        # Back button
        back_btn = Button(text="🏠 Back to Village", size_hint_y=None, height=dp(50), font_size='18sp')
        back_btn.bind(on_release=self.go_back)
        self.layout.add_widget(back_btn)

    def unlock_wizards_tower(self, instance):
        self.upgrades['wizards_tower'] = True
        self.save_upgrades()
        self.build_ui()

    def load_upgrades(self):
        _, upgrades = load_army()
        return upgrades if upgrades is not None else {}

    def save_upgrades(self):
        # Save upgrades with a dummy army (or load the current one if you want to persist units too)
        units, _ = load_army()
        if units is None:
            units = create_mock_roster()
        save_army(units, upgrades=self.upgrades)

    def go_back(self, instance):
        self.manager.current = 'landing'
