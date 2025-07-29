from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.switch import Switch
from kivy.metrics import dp
from kivy.utils import platform

class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Mobile-optimized layout
        padding = dp(20) if platform in ['android', 'ios'] else dp(15)
        spacing = dp(15) if platform in ['android', 'ios'] else dp(10)
        
        # Main layout
        self.layout = BoxLayout(orientation='vertical', padding=padding, spacing=spacing)

        # Title
        title_label = Label(
            text="⚙️ Settings",
            font_size='28sp' if platform in ['android', 'ios'] else '24sp',
            size_hint_y=None,
            height=dp(60) if platform in ['android', 'ios'] else dp(50),
            color=(0.9, 0.9, 0.9, 1)
        )
        self.layout.add_widget(title_label)

        # Settings options
        self.create_setting_option("Sound Effects", True)
        self.create_setting_option("Background Music", True)
        self.create_setting_option("Vibration", platform in ['android', 'ios'])
        self.create_setting_option("Auto-save", True)
        self.create_setting_option("Show Tutorial", True)

        # Spacer
        spacer = Label(size_hint_y=1)
        self.layout.add_widget(spacer)

        # Back button
        button_height = dp(60) if platform in ['android', 'ios'] else dp(50)
        button_font = '20sp' if platform in ['android', 'ios'] else '18sp'
        back_button = Button(
            text="🏠 Back to Village",
            size_hint_y=None,
            height=button_height,
            font_size=button_font
        )
        back_button.bind(on_release=self.go_back)
        self.layout.add_widget(back_button)

        self.add_widget(self.layout)

    def create_setting_option(self, text, default_value):
        """Create a setting option with label and switch."""
        # Container for this setting
        setting_container = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50) if platform in ['android', 'ios'] else dp(40),
            spacing=dp(10)
        )

        # Label
        label = Label(
            text=text,
            font_size='18sp' if platform in ['android', 'ios'] else '16sp',
            size_hint_x=0.7,
            halign='left',
            valign='middle'
        )
        label.bind(size=label.setter('text_size'))
        setting_container.add_widget(label)

        # Switch
        switch = Switch(
            active=default_value,
            size_hint_x=0.3
        )
        switch.bind(active=self.on_setting_changed)
        setting_container.add_widget(switch)

        self.layout.add_widget(setting_container)

    def on_setting_changed(self, instance, value):
        """Handle setting changes."""
        # Here you would save the setting to persistent storage
        print(f"Setting changed: {value}")

    def go_back(self, instance):
        """Return to the landing screen."""
        self.manager.current = 'landing' 