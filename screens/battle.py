from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

class BattleScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Create a layout for the battle screen
        layout = BoxLayout(orientation='vertical')

        # Add a title label
        layout.add_widget(Label(text='Battle Screen', font_size='24sp'))

        # Add a button to return to the landing screen
        back_button = Button(text='Back to Village', size_hint_y=0.2)
        back_button.bind(on_release=self.go_back)
        layout.add_widget(back_button)

        self.add_widget(layout)

    def go_back(self, instance):
        self.manager.current = 'landing'
