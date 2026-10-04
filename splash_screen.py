"""Splash Screen — 10-second intro video (like a phone boot animation).

Plays assets/intro.mp4 full-screen once when the app opens, then fades
into the login screen. If the video can't be played on a device (missing
video provider, bad codec...) it falls back to the animated logo so the
app never gets stuck on a black screen.
"""

import os
from kivy.uix.screenmanager import Screen, FadeTransition
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image as KivyImage
from kivy.graphics import Color, Rectangle
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.utils import get_color_from_hex

VIDEO_SECONDS = 10.0          # length of the intro clip
SAFETY_MARGIN = 0.6           # leave after this extra time even if no EOS event
FALLBACK_SECONDS = 3.2        # logo-only fallback duration

_ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets')
VIDEO_PATH = os.path.join(_ASSETS, 'intro.mp4')
LOGO_PATH = os.path.join(_ASSETS, 'logo.png')


class SplashScreen(Screen):

    def __init__(self, **kw):
        super().__init__(**kw)
        self._done = False
        self._video = None
        self._events = []
        self._build()

    # ── UI ────────────────────────────────────────────────
    def _build(self):
        with self.canvas.before:
            Color(0.02, 0.02, 0.05, 1)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=lambda w, v: setattr(self._bg, 'pos', v),
                  size=lambda w, v: setattr(self._bg, 'size', v))

        self.stack = FloatLayout()
        self.add_widget(self.stack)
        self._build_fallback()

    def _build_fallback(self):
        """Animated logo — only shown if the video can't play."""
        self.fb = BoxLayout(orientation='vertical', padding=30, spacing=16,
                            opacity=0)
        self.fb.add_widget(Label())
        if os.path.exists(LOGO_PATH):
            logo = KivyImage(source=LOGO_PATH, size_hint=(None, None),
                             size=(260, 260), pos_hint={'center_x': 0.5})
        else:
            logo = Label(text="BRO'S", font_size=60, bold=True,
                         color=get_color_from_hex('#FFD700'),
                         size_hint=(None, None), size=(260, 120),
                         pos_hint={'center_x': 0.5})
        self.fb.add_widget(logo)
        for text, col, h in (
                ("BRO'S Engineering Solution Pvt.Ltd.", '#FFFFFF', 36),
                ('Three Friends. One Vision. Endless Innovation.', '#FFD700', 28)):
            l = Label(text=text, font_size=14, color=get_color_from_hex(col),
                      halign='center', valign='middle',
                      size_hint_y=None, height=h)
            l.bind(size=l.setter('text_size'))
            self.fb.add_widget(l)
        self.fb.add_widget(Label())
        self.stack.add_widget(self.fb)

    # ── lifecycle ─────────────────────────────────────────
    def on_enter(self):
        self._done = False
        if os.path.exists(VIDEO_PATH) and self._start_video():
            # watchdog 1: did the video actually produce frames?
            self._events.append(Clock.schedule_once(self._check_started, 2.5))
            # watchdog 2: hard stop so the intro is always ~10 seconds
            self._events.append(
                Clock.schedule_once(self._finish, VIDEO_SECONDS + SAFETY_MARGIN))
        else:
            self._start_fallback()

    def _start_video(self):
        try:
            from kivy.uix.video import Video
            kw = dict(source=VIDEO_PATH, state='play', volume=1.0,
                      options={'eos': 'stop'}, size_hint=(1, 1))
            try:
                v = Video(fit_mode='cover', **kw)     # Kivy >= 2.2: fill screen
            except Exception:
                v = Video(allow_stretch=True, **kw)
            v.bind(eos=lambda *a: self._finish())
            self._video = v
            self.stack.add_widget(v, index=0)
            return True
        except Exception as e:                           # no provider etc.
            print('[splash] video unavailable:', e)
            return False

    def _check_started(self, dt):
        v = self._video
        if v is None or self._done:
            return
        if v.texture is None or v.position <= 0:        # nothing is playing
            print('[splash] video did not start -> fallback')
            self._drop_video()
            self._start_fallback()

    def _start_fallback(self):
        Animation(opacity=1, duration=1.2).start(self.fb)
        self._events.append(Clock.schedule_once(self._finish, FALLBACK_SECONDS))

    def _drop_video(self):
        if self._video is not None:
            try:
                self._video.state = 'stop'
                self._video.unload()
            except Exception:
                pass
            self.stack.remove_widget(self._video)
            self._video = None

    def _finish(self, *a):
        if self._done:
            return
        self._done = True
        for ev in self._events:
            ev.cancel()
        self._events = []
        self._drop_video()
        if self.manager:
            old = self.manager.transition
            self.manager.transition = FadeTransition(duration=0.6)
            self.manager.current = 'login'
            Clock.schedule_once(
                lambda dt: setattr(self.manager, 'transition', old), 1.0)
