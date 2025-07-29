from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.utils import platform

class LandingScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Mobile-optimized padding and spacing
        padding = dp(20) if platform in ['android', 'ios'] else dp(10)
        spacing = dp(15) if platform in ['android', 'ios'] else dp(10)

        # Create the main vertical layout
        main_layout = BoxLayout(orientation='vertical', padding=padding, spacing=spacing)

        # Top: background village image
        village_image = Image(
            source='assets/images/village_bg.png',
            size_hint_y=0.5
        )
        main_layout.add_widget(village_image)

        # Middle: Button Grid - Mobile optimized
        if platform in ['android', 'ios']:
            button_grid = GridLayout(cols=2, spacing=dp(15), size_hint_y=0.3)
            button_height = dp(80)
            font_size = '24sp'
        else:
            button_grid = GridLayout(cols=3, spacing=dp(10), size_hint_y=0.2)
            button_height = dp(60)
            font_size = '20sp'

        # Add buttons and connect them to methods
        battle_button = Button(
            text="⚔️ Battle",
            font_size=font_size,
            size_hint_y=None,
            height=button_height,
            on_release=self.go_to_combat
        )
        units_button = Button(
            text="👥 Units",
            font_size=font_size,
            size_hint_y=None,
            height=button_height,
            on_release=self.go_to_units
        )
        structures_button = Button(
            text="🏰 Structures",
            font_size=font_size,
            size_hint_y=None,
            height=button_height,
            on_release=self.go_to_structures
        )
        settings_button = Button(
            text="⚙️ Settings",
            font_size=font_size,
            size_hint_y=None,
            height=button_height,
            on_release=self.go_to_settings
        )

        button_grid.add_widget(battle_button)
        button_grid.add_widget(units_button)
        button_grid.add_widget(structures_button)
        button_grid.add_widget(settings_button)

        main_layout.add_widget(button_grid)

        # Bottom: Version info label
        version_label = Label(
            text="Shattered Worlds Skirmish v0.1",
            font_size='16sp' if platform in ['android', 'ios'] else '14sp',
            size_hint_y=0.1,
            halign='center',
            valign='middle',
            color=(0.7, 0.7, 0.7, 1)
        )
        main_layout.add_widget(version_label)

        # Add everything to this screen
        self.add_widget(main_layout)

    # Each of these methods tells the ScreenManager to switch screens
    def go_to_battle(self, instance):
        self.manager.current = 'battle'

    def go_to_units(self, instance):
        self.manager.current = 'units'

    def go_to_structures(self, instance):
        self.manager.current = 'structures'

    def go_to_settings(self, instance):
        self.manager.current = 'settings'

    def go_to_combat(self, instance):
        self.manager.current = 'combat'
