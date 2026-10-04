"""Home Dashboard Screen"""

import os
from datetime import datetime
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image as KivyImage
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
from utils.app_state import state
from utils.strings import s
from utils.theme import BTN_BG, BTN_BG_DOWN, readable, mode_icon_text
from utils.theme import (t, hex2rgba, PAD, CARD_PAD, BTN_H, MD, LG, SM, XL,
                          XS, RADIUS, FONT_TEXT, FONT_ICON)
from utils.widgets import Card, btn, lbl, section, icon_btn, ThemeToggle
from utils.icons import icon


# icon name, screen, label
NAV_ITEMS = [
    ('menu_items', 'menu',       'Menu Items'),
    ('display',    'display',    'Display'),
    ('brightness', 'brightness', 'Brightness'),
    ('clock',      'datetime_s', 'Date & Time'),
    ('palette',    'color_s',    'Colors'),
    ('scroll',     'scroll_s',   'Scroll'),
    ('program',    'program',    'Program Editor'),
    ('wifi',       'device',     'Connect'),
    ('help',       'tutorial',   'Tutorial'),
    ('settings',   'settings',   'Settings'),
]


def rgba(h):
    return get_color_from_hex(h)


class HomeScreen(Screen):

    def __init__(self, **kw):
        super().__init__(**kw)
        self._build()

    def _build(self):
        with self.canvas.before:
            Color(*t('bg'))
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=lambda w, v: setattr(self._bg, 'pos', v),
                  size=lambda w, v: setattr(self._bg, 'size', v))

        root = BoxLayout(orientation='vertical')

        # ── Header ─────────────────────────────────────
        hdr = BoxLayout(size_hint_y=None, height=64,
                        padding=[PAD, 0], spacing=10)
        with hdr.canvas.before:
            Color(*hex2rgba(t('header')))
            hdr_r = Rectangle(pos=hdr.pos, size=hdr.size)
        hdr.bind(pos=lambda w, v: setattr(hdr_r, 'pos', v),
                 size=lambda w, v: setattr(hdr_r, 'size', v))

        logo_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'logo.png')
        if os.path.exists(logo_path):
            logo = KivyImage(source=logo_path,
                             size_hint=(None, None), size=(48, 48))
            hdr.add_widget(logo)

        title_box = BoxLayout(orientation='vertical')
        t1 = Label(text="BRO'S LED Controller",
                   font_name=FONT_TEXT, bold=True, font_size=MD,
                   color=hex2rgba(t('accent')),
                   halign='left', valign='middle')
        t1.bind(size=t1.setter('text_size'))
        self.conn_lbl = Label(text='Not Connected',
                               font_name=FONT_TEXT,
                               font_size=XS, color=hex2rgba(t('sub')),
                               halign='left', valign='middle')
        self.conn_lbl.bind(size=self.conn_lbl.setter('text_size'))
        title_box.add_widget(t1)
        title_box.add_widget(self.conn_lbl)
        hdr.add_widget(title_box)

        hdr.add_widget(Label())  # spacer
        hdr.add_widget(ThemeToggle())

        # Power/logout button — text label, not an icon-only glyph,
        # so its purpose is unambiguous on every device
        logout_btn = Button(
            text='Logout', font_name=FONT_TEXT, bold=True,
            font_size=XS, size_hint=(None, None), size=(66, 36),
            color=rgba('#FFFFFF'),
            background_normal=BTN_BG, background_down=BTN_BG_DOWN, background_color=rgba('#C62828'),
        )
        logout_btn.bind(on_press=self._logout)
        hdr.add_widget(logout_btn)

        root.add_widget(hdr)

        # ── Scrollable body ─────────────────────────────
        sv = ScrollView()
        body = BoxLayout(orientation='vertical', padding=PAD,
                         spacing=12, size_hint_y=None)
        body.bind(minimum_height=body.setter('height'))

        # Welcome + clear, legible date/time card
        self.welcome_card = Card(size_hint_y=None, height=112,
                                  orientation='vertical',
                                  padding=CARD_PAD, spacing=4)
        self.user_lbl = Label(
            text=f"Welcome, {state.username}!",
            font_name=FONT_TEXT, bold=True, font_size=MD,
            color=hex2rgba(t('accent')),
            halign='left', valign='middle',
            size_hint_y=None, height=24,
        )
        self.user_lbl.bind(size=self.user_lbl.setter('text_size'))
        self.welcome_card.add_widget(self.user_lbl)

        datetime_row = BoxLayout(size_hint_y=None, height=46, spacing=10)
        self.time_lbl = Label(
            text='', font_name=FONT_TEXT, bold=True, font_size=24,
            color=hex2rgba(t('accent2')),
            halign='left', valign='middle',
        )
        self.time_lbl.bind(size=self.time_lbl.setter('text_size'))
        self.date_lbl = Label(
            text=datetime.now().strftime('%a, %d %b %Y'),
            font_name=FONT_TEXT, font_size=MD, color=hex2rgba(t('text')),
            halign='right', valign='middle',
        )
        self.date_lbl.bind(size=self.date_lbl.setter('text_size'))
        datetime_row.add_widget(self.time_lbl)
        datetime_row.add_widget(self.date_lbl)
        self.welcome_card.add_widget(datetime_row)
        body.add_widget(self.welcome_card)

        # Current message card
        msg_card = Card(size_hint_y=None, height=80,
                        orientation='vertical',
                        padding=CARD_PAD, spacing=4)
        msg_card.add_widget(Label(
            text='Current Display Message',
            font_name=FONT_TEXT, font_size=XS, color=hex2rgba(t('sub')),
            size_hint_y=None, height=20,
            halign='left', valign='middle',
        ))
        self.msg_lbl = Label(
            text=state.text_content,
            font_name=FONT_TEXT, font_size=MD, color=hex2rgba(readable(state.text_color)),
            size_hint_y=None, height=30,
            halign='left', valign='middle',
        )
        self.msg_lbl.bind(size=self.msg_lbl.setter('text_size'))
        msg_card.add_widget(self.msg_lbl)
        body.add_widget(msg_card)

        # Quick menu items
        body.add_widget(section('Quick Send — Menu Items'))
        self.menu_box = BoxLayout(orientation='vertical',
                                   size_hint_y=None, spacing=6)
        self.menu_box.bind(minimum_height=self.menu_box.setter('height'))
        self._rebuild_menu()
        body.add_widget(self.menu_box)

        # Nav grid — icon + readable label on every button
        body.add_widget(section('All Features'))
        grid = GridLayout(cols=2, spacing=8,
                          size_hint_y=None, height=5 * 68)
        COLORS = ['#1565C0','#4A148C','#1B5E20',
                  '#BF360C','#006064','#37474F',
                  '#4E342E','#263238','#880E4F','#6A1B9A']
        for i, (icon_name, scr, lbl_text) in enumerate(NAV_ITEMS):
            b = icon_btn(icon_name, lbl_text, bg=COLORS[i % len(COLORS)],
                         fg='#FFFFFF', height=64, fs=SM)
            b.bind(on_press=lambda x, sc=scr: self._go(sc))
            grid.add_widget(b)
        body.add_widget(grid)

        sv.add_widget(body)
        root.add_widget(sv)

        # ── Send bar ────────────────────────────────────
        bar = BoxLayout(size_hint_y=None, height=66,
                        padding=[PAD, 8], spacing=10)
        with bar.canvas.before:
            Color(*hex2rgba(t('header')))
            bar_r = Rectangle(pos=bar.pos, size=bar.size)
        bar.bind(pos=lambda w, v: setattr(bar_r, 'pos', v),
                 size=lambda w, v: setattr(bar_r, 'size', v))

        lang_btn = Button(
            text='EN/TA', font_name=FONT_TEXT, bold=True,
            font_size=SM, size_hint_x=0.22, height=50,
            color=rgba(t('accent2')),
            background_color=(0,0,0,0), background_normal=BTN_BG, background_down=BTN_BG_DOWN,
        )
        lang_btn.bind(on_press=self._toggle_lang)

        send_btn = btn('SEND TO BOARD', bg=t('accent'), fg='#000000',
                       height=50, fs=LG, bold=True)
        send_btn.size_hint_x = 0.78
        send_btn.bind(on_press=self._send)

        bar.add_widget(lang_btn)
        bar.add_widget(send_btn)
        root.add_widget(bar)

        self.add_widget(root)

        # Clock ticker
        Clock.schedule_interval(self._tick, 1)

    def _rebuild_menu(self):
        self.menu_box.clear_widgets()
        for item in state.menu_items[:5]:  # show top 5
            row = BoxLayout(size_hint_y=None, height=46, spacing=8)

            name_lbl = Label(
                text=f'{item["name"]}  {item["price"]}',
                font_name=FONT_TEXT, bold=True, font_size=SM,
                color=rgba(readable(item.get('color', '#FFFFFF'))),
                halign='left', valign='middle',
            )
            name_lbl.bind(size=name_lbl.setter('text_size'))

            send_b = Button(
                text='Send', font_name=FONT_TEXT, bold=True, font_size=XS,
                size_hint=(None, None), size=(72, 36),
                color=rgba('#000000'),
                background_normal=BTN_BG, background_down=BTN_BG_DOWN, background_color=rgba('#00E676'),
            )
            send_b.bind(on_press=lambda x, it=item: self._send_item(it))
            row.add_widget(name_lbl)
            row.add_widget(send_b)
            self.menu_box.add_widget(row)

    def _send_item(self, item):
        state.text_content = f'{item["name"]}  {item["price"]}'
        state.text_color   = item.get('color', '#FFD700')
        self._send(None)

    def _send(self, _):
        from commands.led_commands import get_board
        board = get_board(state.device_ip)
        if board.connect():
            board.sync_time()
            board.set_brightness(state.brightness)
            board.send_content(state)
            board.disconnect()
            self.conn_lbl.text  = 'Sent to Board!'
            self.conn_lbl.color = hex2rgba(t('ok'))
            Clock.schedule_once(lambda dt: self._reset_conn_lbl(), 3)

    def _reset_conn_lbl(self):
        if state.is_connected:
            self.conn_lbl.text  = state.device_ip
            self.conn_lbl.color = hex2rgba(t('ok'))
        else:
            self.conn_lbl.text  = 'Not Connected'
            self.conn_lbl.color = hex2rgba(t('sub'))

    def _tick(self, dt):
        now = datetime.now()
        fmt = '%I:%M:%S %p' if state.clock_format == '12h' else '%H:%M:%S'
        self.time_lbl.text = now.strftime(fmt)
        self.date_lbl.text = now.strftime('%a, %d %b %Y')

    def _go(self, name):
        self.manager.current = name

    def _logout(self, _):
        state.logged_in = False
        state.username  = ''
        self.manager.current = 'login'

    def _toggle_lang(self, _):
        state.language = 'ta' if state.language == 'en' else 'en'

    def on_enter(self):
        self.user_lbl.text = f"Welcome, {state.username}!"
        self.msg_lbl.text  = state.text_content
        self.msg_lbl.color = hex2rgba(readable(state.text_color))
        self._rebuild_menu()
        if state.is_connected:
            self.conn_lbl.text  = state.device_ip
            self.conn_lbl.color = hex2rgba(t('ok'))
