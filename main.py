from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivy.core.window import Window
from kivy.utils import platform

# Import all the screens we'll use
from screens.landing import LandingScreen
from screens.battle import BattleScreen
from screens.units import UnitsScreen
from screens.structures import StructuresScreen
from screens.level_up import LevelUpScreen
from screens.combat import CombatScreen
from screens.settings import SettingsScreen


class VillageGameApp(App):
    def build(self):
        # Mobile-specific configurations
        if platform == 'android':
            # Hide status bar on Android
            from android.runnable import run_on_ui_thread
            from jnius import autoclass
            
            @run_on_ui_thread
            def hide_status_bar():
                activity = autoclass('org.kivy.android.PythonActivity').mActivity
                activity.getWindow().setFlags(1024, 1024)  # FLAG_FULLSCREEN
            
            hide_status_bar()
        
        # Set window properties for mobile
        if platform in ['android', 'ios']:
            Window.fullscreen = 'auto'
            Window.softinput_mode = 'below_target'
        
        # Create a ScreenManager to handle screen switching
        sm = ScreenManager(transition=FadeTransition())

        # Add each screen to the manager, using a unique name for each
        sm.add_widget(LandingScreen(name='landing'))
        sm.add_widget(BattleScreen(name='battle'))
        sm.add_widget(UnitsScreen(name='units'))
        sm.add_widget(StructuresScreen(name='structures'))
        sm.add_widget(LevelUpScreen(name='level_up'))
        sm.add_widget(CombatScreen(name='combat'))
        sm.add_widget(SettingsScreen(name='settings'))
        
        # Return the root widget (the ScreenManager)
        return sm

if __name__ == '__main__':
    VillageGameApp().run()
