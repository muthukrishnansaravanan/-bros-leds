"""Login / Signup Screen"""

import os
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image as KivyImage
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.utils import get_color_from_hex
from utils.app_state import state
from utils.theme import (PAD, BTN_H, MD, LG, SM, XL, RADIUS, FONT_TEXT,
                         BTN_BG, BTN_BG_DOWN, t)
from utils.widgets import PasswordField, ThemeToggle, Card


class _Pal:
    """Colours resolved from the ACTIVE theme each time the screen is built."""
    C_BG = property(lambda self: t('bg'))
    C_CARD  = property(lambda self: t('card'))
    C_GOLD  = property(lambda self: t('accent'))
    C_BLUE  = property(lambda self: t('accent2'))
    C_WHITE = property(lambda self: t('text'))
    C_GRAY  = property(lambda self: t('sub'))
    C_RED   = property(lambda self: t('btn_del'))
    C_GREEN = property(lambda self: t('ok'))
    C_INPUT = property(lambda self: t('input_bg'))
    C_TAB_OFF = property(lambda self: t('header'))
    C_ON_GOLD = property(lambda self: '#000000')
_P = _Pal()


def rgba(h):
    return get_color_from_hex(h)


class LoginScreen(Screen):

    def __init__(self, **kw):
        super().__init__(**kw)
        self._mode = 'login'   # 'login' or 'signup'
        self._build()

    def _build(self):
        with self.canvas.before:
            Color(*_P.C_BG)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=lambda w, v: setattr(self._bg, 'pos', v),
                  size=lambda w, v: setattr(self._bg, 'size', v))

        self.root_box = BoxLayout(orientation='vertical',
                                   padding=[PAD*2, 0],
                                   spacing=10)

        top = BoxLayout(size_hint_y=None, height=52, padding=[0, 8])
        top.add_widget(Label())
        top.add_widget(ThemeToggle())
        self.root_box.add_widget(top)

        # ── Logo area ──────────────────────────────────
        logo_box = BoxLayout(size_hint_y=None, height=190,
                              orientation='vertical', spacing=6)

        logo_path = os.path.join(os.path.dirname(__file__),
                                 '..', 'assets', 'logo.png')
        if os.path.exists(logo_path):
            logo_img = KivyImage(
                source=logo_path,
                size_hint=(None, None), size=(140, 140),
                pos_hint={'center_x': 0.5},
            )
            logo_box.add_widget(logo_img)
        else:
            logo_box.add_widget(Label(
                text="BRO'S", font_name=FONT_TEXT, bold=True,
                font_size=50, color=rgba(_P.C_GOLD),
            ))

        co_lbl = Label(
            text="BRO'S Engineering Solution Pvt.Ltd.",
            font_name=FONT_TEXT, bold=True, font_size=SM,
            color=rgba(_P.C_WHITE), halign='center', valign='middle',
            size_hint_y=None, height=24,
        )
        co_lbl.bind(size=co_lbl.setter('text_size'))
        logo_box.add_widget(co_lbl)

        self.root_box.add_widget(logo_box)

        # ── Tab buttons ────────────────────────────────
        tab_row = BoxLayout(size_hint_y=None, height=44, spacing=6)
        self.login_tab = Button(
            text='LOGIN', font_name=FONT_TEXT, bold=True,
            font_size=MD, color=rgba('#000000'),
            background_normal=BTN_BG, background_down=BTN_BG_DOWN, background_color=rgba(_P.C_GOLD),
        )
        self.signup_tab = Button(
            text='SIGN UP', font_name=FONT_TEXT, bold=True,
            font_size=MD, color=rgba(_P.C_GOLD),
            background_normal=BTN_BG, background_down=BTN_BG_DOWN, background_color=rgba(_P.C_TAB_OFF),
        )
        self.login_tab.bind(on_press=lambda x: self._switch_mode('login'))
        self.signup_tab.bind(on_press=lambda x: self._switch_mode('signup'))
        tab_row.add_widget(self.login_tab)
        tab_row.add_widget(self.signup_tab)
        self.root_box.add_widget(tab_row)

        # ── Card ───────────────────────────────────────
        self.card = BoxLayout(
            orientation='vertical',
            size_hint_y=None, height=330,
            padding=RADIUS, spacing=10,
        )
        with self.card.canvas.before:
            Color(*rgba(_P.C_CARD))
            self._card_rect = RoundedRectangle(
                pos=self.card.pos, size=self.card.size,
                radius=[RADIUS]*4)
        self.card.bind(
            pos=lambda w, v: setattr(self._card_rect, 'pos', v),
            size=lambda w, v: setattr(self._card_rect, 'size', v))

        # Username
        un_lbl = Label(text='Username', font_name=FONT_TEXT, font_size=SM,
                       color=rgba(_P.C_GRAY), size_hint_y=None, height=22,
                       halign='left', valign='middle')
        un_lbl.bind(size=un_lbl.setter('text_size'))
        self.card.add_widget(un_lbl)

        self.un_input = TextInput(
            hint_text='Enter username',
            font_name=FONT_TEXT,
            font_size=MD, multiline=False,
            size_hint_y=None, height=46,
            background_color=rgba(_P.C_INPUT),
            foreground_color=rgba(_P.C_WHITE),
            cursor_color=rgba(_P.C_GOLD),
            hint_text_color=rgba(_P.C_GRAY),
        )
        self.card.add_widget(self.un_input)

        # Password — with SHOW/HIDE toggle so the user can verify it
        pw_lbl = Label(text='Password', font_name=FONT_TEXT, font_size=SM,
                       color=rgba(_P.C_GRAY), size_hint_y=None, height=22,
                       halign='left', valign='middle')
        pw_lbl.bind(size=pw_lbl.setter('text_size'))
        self.card.add_widget(pw_lbl)

        self.pw_field = PasswordField(hint_text='Enter password')
        self.card.add_widget(self.pw_field)

        # Confirm password (signup only) — also with SHOW/HIDE
        self.cp_lbl = Label(text='Confirm Password', font_name=FONT_TEXT,
                            font_size=SM, color=rgba(_P.C_GRAY),
                            size_hint_y=None, height=22,
                            halign='left', valign='middle')
        self.cp_lbl.bind(size=self.cp_lbl.setter('text_size'))
        self.cp_lbl.opacity = 0
        self.card.add_widget(self.cp_lbl)

        self.cp_field = PasswordField(hint_text='Confirm password')
        self.cp_field.opacity = 0
        self.cp_field.disabled = True
        self.card.add_widget(self.cp_field)

        self.root_box.add_widget(self.card)

        # Status label
        self.status_lbl = Label(
            text='', font_name=FONT_TEXT, font_size=SM,
            color=rgba(_P.C_RED),
            size_hint_y=None, height=26,
            halign='center', valign='middle',
        )
        self.status_lbl.bind(size=self.status_lbl.setter('text_size'))
        self.root_box.add_widget(self.status_lbl)

        # Action button
        self.action_btn = Button(
            text='LOGIN', font_name=FONT_TEXT, bold=True,
            size_hint_y=None, height=BTN_H + 4,
            font_size=LG, color=rgba('#000000'),
            background_normal=BTN_BG, background_down=BTN_BG_DOWN, background_color=rgba(_P.C_GOLD),
        )
        self.action_btn.bind(on_press=self._action)
        self.root_box.add_widget(self.action_btn)

        # Language toggle — plain text, no flag emoji (flags never
        # render correctly without a large colour-emoji font)
        lang_btn = Button(
            text='Switch to Tamil / English',
            font_name=FONT_TEXT, font_size=SM, color=rgba(_P.C_BLUE),
            background_color=(0, 0, 0, 0), background_normal=BTN_BG, background_down=BTN_BG_DOWN,
            size_hint_y=None, height=36,
        )
        lang_btn.bind(on_press=self._toggle_lang)
        self.root_box.add_widget(lang_btn)

        self.root_box.add_widget(Label())  # spacer

        self.add_widget(self.root_box)
        self._switch_mode(self._mode)

    def _switch_mode(self, mode):
        self._mode = mode
        if mode == 'login':
            self.login_tab.background_color  = get_color_from_hex(_P.C_GOLD)
            self.login_tab.color             = get_color_from_hex('#000000')
            self.signup_tab.background_color = get_color_from_hex(_P.C_TAB_OFF)
            self.signup_tab.color            = get_color_from_hex(_P.C_GOLD)
            self.cp_lbl.opacity    = 0
            self.cp_field.opacity  = 0
            self.cp_field.disabled = True
            self.action_btn.text   = 'LOGIN'
            self.card.height       = 290
        else:
            self.login_tab.background_color  = get_color_from_hex(_P.C_TAB_OFF)
            self.login_tab.color             = get_color_from_hex(_P.C_GOLD)
            self.signup_tab.background_color = get_color_from_hex(_P.C_GOLD)
            self.signup_tab.color            = get_color_from_hex('#000000')
            self.cp_lbl.opacity    = 1
            self.cp_field.opacity  = 1
            self.cp_field.disabled = False
            self.action_btn.text   = 'CREATE ACCOUNT'
            self.card.height       = 330

    def _action(self, _):
        un = self.un_input.text.strip()
        pw = self.pw_field.text.strip()
        self.status_lbl.color = get_color_from_hex(_P.C_RED)

        if not un or not pw:
            self.status_lbl.text = 'Please fill all fields'
            return

        if self._mode == 'login':
            if un in state.users and state.users[un] == pw:
                state.logged_in = True
                state.username  = un
                self.status_lbl.text  = ''
                self.manager.current  = 'home'
            else:
                self.status_lbl.text = 'Invalid username or password'

        else:  # signup
            cp = self.cp_field.text.strip()
            if pw != cp:
                self.status_lbl.text = 'Passwords do not match'
                return
            if un in state.users:
                self.status_lbl.text = 'Username already exists'
                return
            state.users[un] = pw
            state.save()
            self.status_lbl.color = get_color_from_hex(_P.C_GREEN)
            self.status_lbl.text  = 'Account created! Please login.'
            self._switch_mode('login')

    def _toggle_lang(self, _):
        state.language = 'ta' if state.language == 'en' else 'en'

    def on_enter(self):
        self.un_input.text = ''
        self.pw_field.text = ''
        self.cp_field.text = ''
        self.status_lbl.text = ''
