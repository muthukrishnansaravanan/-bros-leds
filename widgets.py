"""Reusable widgets"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, RoundedRectangle, Rectangle, Line
from utils.theme import BTN_BG, BTN_BG_DOWN, readable, mode_icon_text
from utils.theme import (t, hex2rgba, PAD, CARD_PAD, BTN_H, MD, LG, SM, XS,
                          RADIUS, FONT_TEXT, FONT_ICON)
from utils.icons import icon


class Card(BoxLayout):
    def __init__(self, radius=RADIUS, **kw):
        super().__init__(**kw)
        self._r = radius
        self.bind(pos=self._draw, size=self._draw)

    def _draw(self, *a):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*hex2rgba(t('card')))
            RoundedRectangle(pos=self.pos, size=self.size,
                             radius=[self._r] * 4)
            # soft outline so cards stay visible on the light theme
            Color(0.5, 0.55, 0.65, 0.35 if not t('is_dark') else 0.18)
            Line(rounded_rectangle=(self.x, self.y, self.width, self.height,
                                    self._r), width=1)


class ThemeToggle(Button):
    """Small Dark/Light switch shown on every page."""

    def __init__(self, **kw):
        super().__init__(
            text=mode_icon_text(), font_name=FONT_ICON, font_size=LG,
            size_hint=(None, None), size=(44, 40),
            color=hex2rgba(t('accent')),
            background_normal=BTN_BG, background_down=BTN_BG_DOWN,
            background_color=hex2rgba(t('card')), **kw)
        self.bind(on_release=self._flip)

    def _flip(self, *_):
        from kivy.app import App
        app = App.get_running_app()
        if app:
            app.toggle_mode()


class HeaderBar(BoxLayout):
    """Top bar with title. Always shows a back button unless the screen
    is explicitly a root screen (show_back=False) — every other screen
    in the app must be reachable from a visible back control.

    IMPORTANT: pass the Screen instance itself (`self`) as `screen`, not
    `self.manager`. HeaderBar is built from inside a Screen's __init__,
    and at that point the screen has not been added to a ScreenManager
    yet, so `self.manager` is still None — any button bound to it at
    construction time would silently never navigate anywhere. Resolving
    `screen.manager` lazily, at the moment the button is pressed,
    sidesteps that entirely."""

    def __init__(self, title, screen=None, back='home', show_back=True,
                 icon_name=None, **kw):
        kw.setdefault('size_hint_y', None)
        kw.setdefault('height', 62)
        kw.setdefault('padding', [PAD, 0])
        kw.setdefault('spacing', 8)
        super().__init__(**kw)
        self._draw_bg()
        self.bind(pos=self._draw_bg, size=self._draw_bg)

        if show_back and screen is not None:
            bb = Button(
                text=icon('back'), font_name=FONT_ICON,
                size_hint=(None, None), size=(44, 44),
                font_size=LG, color=hex2rgba(t('text')),
                background_color=(0, 0, 0, 0), background_normal=BTN_BG, background_down=BTN_BG_DOWN,
            )

            def _go_back(_x, _screen=screen, _back=back):
                if _screen.manager:
                    _screen.manager.current = _back

            bb.bind(on_press=_go_back)
            self.add_widget(bb)

        title_row = BoxLayout(spacing=6)
        if icon_name:
            title_row.add_widget(Label(
                text=icon(icon_name), font_name=FONT_ICON,
                font_size=LG, color=hex2rgba(t('accent')),
                size_hint_x=None, width=26,
            ))
        lbl_widget = Label(
            text=title, font_name=FONT_TEXT, bold=True,
            font_size=LG, color=hex2rgba(t('accent')),
            halign='left', valign='middle',
        )
        lbl_widget.bind(size=lbl_widget.setter('text_size'))
        title_row.add_widget(lbl_widget)
        self.add_widget(title_row)
        self.add_widget(ThemeToggle())

    def _draw_bg(self, *a):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*hex2rgba(t('header')))
            Rectangle(pos=self.pos, size=self.size)
            Color(*hex2rgba(t('accent'))[:3], 0.55)
            Rectangle(pos=(self.x, self.y), size=(self.width, 2))


def btn(text, bg=None, fg='#000000', height=BTN_H, fs=MD, bold=False):
    """Plain text button. Bold defaults to False — only the main
    call-to-action on a screen should be bold."""
    if bg is None:
        bg = t('btn_ok')
    b = Button(
        text=text, font_name=FONT_TEXT, bold=bold,
        size_hint_y=None, height=height,
        font_size=fs,
        color=hex2rgba(fg),
        background_normal=BTN_BG, background_down=BTN_BG_DOWN,
        background_color=hex2rgba(bg),
    )
    return b


def icon_btn(icon_name, label_text, bg=None, fg='#FFFFFF',
             height=BTN_H, fs=SM, icon_fs=None):
    """A button that shows a real vector-safe icon ABOVE readable text,
    so every button is visually distinct (fixes icons collapsing into
    one blank glyph) and still usable even without recognising the icon."""
    if bg is None:
        bg = t('btn_info')
    if icon_fs is None:
        icon_fs = fs + 8
    b = Button(
        text=f'{icon(icon_name)}\n{label_text}',
        markup=False, halign='center',
        size_hint_y=None, height=height,
        font_size=fs, color=hex2rgba(fg),
        background_normal=BTN_BG, background_down=BTN_BG_DOWN, background_color=hex2rgba(bg),
    )
    # Buttons only take a single font; DejaVuSans also renders plain
    # Latin text cleanly (non-bold), so it's safe to use for the whole
    # icon+label button rather than mixing fonts within one Label.
    b.font_name = FONT_ICON
    return b


def lbl(text, color=None, fs=MD, bold=False, halign='left', height=None,
        font_name=None):
    if color is None:
        color = t('text')
    l = Label(
        text=text, font_name=font_name or FONT_TEXT, bold=bold,
        font_size=fs, color=hex2rgba(color),
        halign=halign, valign='middle',
    )
    kw_height = height
    if kw_height:
        l.size_hint_y = None
        l.height = kw_height
    l.bind(size=l.setter('text_size'))
    return l


def icon_lbl(icon_name, color=None, fs=MD):
    if color is None:
        color = t('accent')
    return Label(text=icon(icon_name), font_name=FONT_ICON,
                 font_size=fs, color=hex2rgba(color),
                 size_hint_x=None, width=fs + 14)


def section(text):
    return lbl(text.upper(), color=t('sub'), fs=SM, height=26)


class PasswordField(BoxLayout):
    """A password TextInput with a 'SHOW/HIDE' toggle button, so the
    user can verify what they typed before submitting."""

    def __init__(self, hint_text='Enter password', **kw):
        kw.setdefault('size_hint_y', None)
        kw.setdefault('height', 46)
        kw.setdefault('spacing', 6)
        super().__init__(**kw)

        self.input = TextInput(
            hint_text=hint_text, password=True,
            font_size=MD, multiline=False,
            font_name=FONT_TEXT,
            background_color=hex2rgba(t('input_bg')),
            foreground_color=hex2rgba(t('text')),
            cursor_color=hex2rgba(t('accent')),
            hint_text_color=hex2rgba(t('sub')),
        )
        self.add_widget(self.input)

        self.toggle_btn = Button(
            text='SHOW', font_name=FONT_TEXT, bold=True,
            font_size=XS, size_hint_x=None, width=62,
            color=hex2rgba('#000000'),
            background_normal=BTN_BG, background_down=BTN_BG_DOWN, background_color=hex2rgba(t('accent2')),
        )
        self.toggle_btn.bind(on_press=self._toggle)
        self.add_widget(self.toggle_btn)

    def _toggle(self, _):
        showing = not self.input.password
        self.input.password = showing
        self.toggle_btn.text = 'HIDE' if not showing else 'SHOW'

    @property
    def text(self):
        return self.input.text

    @text.setter
    def text(self, v):
        self.input.text = v
