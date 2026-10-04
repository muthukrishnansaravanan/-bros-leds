"""
BRO'S LED Controller
Hotel Menu Display App
Python + Kivy | WF2 P10 RGB Board | TCP Port 9527
"""

import os
os.environ['KIVY_NO_CONSOLELOG'] = '0'

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle

# Simulate phone size on desktop
Window.size = (420, 780)

from utils.app_state import state
from utils.theme import t, is_dark_theme
from screens.splash_screen import SplashScreen
from screens.login_screen  import LoginScreen
from screens.home_screen   import HomeScreen
from screens.menu_screen   import MenuScreen
from screens.other_screens import (
    DisplayScreen, BrightnessScreen, DateTimeScreen,
    ColorScreen, ScrollScreen, DeviceScreen,
    ProgramEditorScreen, TutorialScreen, SettingsScreen,
)


class BrosLedApp(App):
    title = "BRO'S LED Controller"
    icon  = os.path.join('assets', 'logo.png')

    def build(self):
        # Load saved settings BEFORE any screen is built so the saved
        # Dark/Light theme is applied from the very first frame.
        state.load()
        Window.clearcolor = t('bg')
        sm = ScreenManager(transition=FadeTransition(duration=0.25))

        sm.add_widget(SplashScreen(name='splash'))
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(DisplayScreen(name='display'))
        sm.add_widget(BrightnessScreen(name='brightness'))
        sm.add_widget(DateTimeScreen(name='datetime_s'))
        sm.add_widget(ColorScreen(name='color_s'))
        sm.add_widget(ScrollScreen(name='scroll_s'))
        sm.add_widget(DeviceScreen(name='device'))
        sm.add_widget(ProgramEditorScreen(name='program'))
        sm.add_widget(TutorialScreen(name='tutorial'))
        sm.add_widget(SettingsScreen(name='settings'))

        self.sm = sm
        return sm

    # ── Live theme switching ──────────────────────────────
    def apply_theme(self):
        """Re-skin every page with state.theme (no restart needed)."""
        from kivy.clock import Clock
        Window.clearcolor = t('bg')
        for scr in self.sm.screens:
            if scr.name == 'splash':
                continue
            if hasattr(scr, '_tick'):
                Clock.unschedule(scr._tick)
            scr.clear_widgets()
            # Screen is a RelativeLayout: its canvas.before holds the
            # PushMatrix/Translate that position it, so only remove the
            # background Color/Rectangle that _build() drew.
            for ins in list(scr.canvas.before.children):
                if isinstance(ins, (Color, Rectangle)):
                    scr.canvas.before.remove(ins)
            scr._build()
        cur = self.sm.current_screen
        if cur and hasattr(cur, 'on_enter'):
            cur.on_enter()

    def toggle_mode(self):
        """Quick Dark <-> Light switch used by the header button."""
        state.theme = 'light' if is_dark_theme() else 'dark'
        state.save()
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: self.apply_theme(), 0)

    def on_stop(self):
        from utils.app_state import state
        state.save()


if __name__ == '__main__':
    BrosLedApp().run()
