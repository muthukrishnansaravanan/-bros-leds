"""
All remaining screens:
DisplayScreen, BrightnessScreen, DateTimeScreen,
ColorScreen, ScrollScreen, DeviceScreen,
TutorialScreen, SettingsScreen
"""

import os
import threading
from datetime import datetime
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.textinput import TextInput
from kivy.uix.switch import Switch
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
from utils.app_state import state
from utils.strings import s
from utils.theme import BTN_BG, BTN_BG_DOWN, readable, mode_icon_text
from utils.theme import (t, hex2rgba, PAD, CARD_PAD, BTN_H, MD, LG, SM, XS,
                          XL, XXL, RADIUS, FONT_TEXT, FONT_ICON)
from utils.widgets import Card, HeaderBar, btn, lbl, section
from utils.icons import icon


def rgba(h): return get_color_from_hex(h)


def bg_screen(screen):
    with screen.canvas.before:
        Color(*t('bg'))
        r = Rectangle(pos=screen.pos, size=screen.size)
    screen.bind(pos=lambda w, v: setattr(r, 'pos', v),
                size=lambda w, v: setattr(r, 'size', v))


def toggle_row(options, current, on_pick):
    """Build a row of toggle buttons; returns (row_widget, btn_dict)."""
    row = BoxLayout(size_hint_y=None, height=48, spacing=8)
    btns = {}
    for lab, val in options:
        b = Button(
            text=lab, font_name=FONT_TEXT, bold=True, font_size=SM,
            color=rgba('#000000' if val == current else '#FFFFFF'),
            background_normal=BTN_BG, background_down=BTN_BG_DOWN,
            background_color=rgba(t('accent') if val == current else t('btn_info')),
        )
        b.bind(on_press=lambda x, v=val: on_pick(v))
        btns[val] = b
        row.add_widget(b)
    return row, btns


# ══════════════════════════════════════════════════════
# DISPLAY SCREEN
# ══════════════════════════════════════════════════════

QUICK_MSGS = [
    "Welcome to Our Hotel!",
    "Today's Special — Ask Us!",
    "Dine In / Take Away",
    "Free Home Delivery",
    "Open 7AM – 10PM",
    "Wi-Fi Password: hotel123",
    "Thank You! Visit Again!",
    "Fresh Food Every Day",
]


class DisplayScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self._build()

    def _build(self):
        bg_screen(self)
        root = BoxLayout(orientation='vertical')
        root.add_widget(HeaderBar('Display Message', self, icon_name='display'))

        body = BoxLayout(orientation='vertical', padding=PAD, spacing=10)

        body.add_widget(section('Type Your Message'))
        self.txt = TextInput(
            text=state.text_content, multiline=True,
            font_name=FONT_TEXT, font_size=LG, size_hint_y=None, height=120,
            background_color=rgba(t('input_bg')),
            foreground_color=rgba(t('text')),
            cursor_color=rgba(t('accent')),
            hint_text='Enter display message...',
        )
        body.add_widget(self.txt)

        body.add_widget(section('Font Size'))
        sr = BoxLayout(size_hint_y=None, height=44, spacing=10)
        self.sz_lbl = Label(text=str(state.text_size), font_name=FONT_TEXT,
                             font_size=MD, color=hex2rgba(t('accent')), size_hint_x=0.15)
        self.sz_sl = Slider(min=14, max=48, value=state.text_size,
                             size_hint_x=0.85)
        self.sz_sl.bind(value=lambda w, v: setattr(self.sz_lbl, 'text', str(int(v))))
        sr.add_widget(self.sz_lbl)
        sr.add_widget(self.sz_sl)
        body.add_widget(sr)

        body.add_widget(section('Quick Messages'))
        grid = GridLayout(cols=2, spacing=6, size_hint_y=None, height=200)
        for q in QUICK_MSGS:
            b = Button(text=q, font_name=FONT_TEXT, font_size=XS, color=rgba('#FFFFFF'),
                       background_normal=BTN_BG, background_down=BTN_BG_DOWN, background_color=rgba('#1A3A5C'),
                       halign='center', text_size=(None, None))
            b.bind(on_press=lambda x, txt=q: setattr(self.txt, 'text', txt))
            grid.add_widget(b)
        body.add_widget(grid)

        body.add_widget(Label())
        save_b = btn('Save Message', bg=t('btn_ok'), fg='#000000', bold=True)
        save_b.bind(on_press=self._save)
        body.add_widget(save_b)

        root.add_widget(body)
        self.add_widget(root)

    def _save(self, _):
        state.text_content = self.txt.text.strip() or state.text_content
        state.text_size    = int(self.sz_sl.value)
        self.manager.current = 'home'

    def on_enter(self):
        self.txt.text      = state.text_content
        self.sz_sl.value   = state.text_size


# ══════════════════════════════════════════════════════
# BRIGHTNESS SCREEN
# ══════════════════════════════════════════════════════

class BrightnessScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self._build()

    def _build(self):
        bg_screen(self)
        root = BoxLayout(orientation='vertical')
        root.add_widget(HeaderBar('Brightness', self, icon_name='brightness'))

        body = BoxLayout(orientation='vertical', padding=PAD*2, spacing=20)

        # Big brightness display
        self.big_lbl = Label(
            text=f'{state.brightness}%',
            font_name=FONT_TEXT, bold=True,
            font_size=70, color=hex2rgba(t('accent')),
            size_hint_y=None, height=120,
            halign='center', valign='middle',
        )
        body.add_widget(self.big_lbl)

        # Sun icon row
        sun_row = BoxLayout(size_hint_y=None, height=50, spacing=10)
        sun_row.add_widget(Label(text=icon('bright_lo'), font_name=FONT_ICON,
                                  font_size=LG, color=hex2rgba(t('sub')),
                                  size_hint_x=0.15, halign='center'))
        self.br_sl = Slider(
            min=0, max=100, value=state.brightness, step=1,
            size_hint_x=0.7,
        )
        self.br_sl.bind(value=self._on_slider)
        sun_row.add_widget(self.br_sl)
        sun_row.add_widget(Label(text=icon('bright_hi'), font_name=FONT_ICON,
                                  font_size=LG, color=hex2rgba(t('accent')),
                                  size_hint_x=0.15, halign='center'))
        body.add_widget(sun_row)

        # Quick preset buttons
        body.add_widget(section('Quick Presets'))
        prow = BoxLayout(size_hint_y=None, height=52, spacing=8)
        for label, val in [('Night 20%', 20), ('Dim 40%', 40),
                            ('Normal 70%', 70), ('Full 100%', 100)]:
            b = Button(text=label, font_name=FONT_TEXT, font_size=XS, color=rgba('#FFFFFF'),
                       background_normal=BTN_BG, background_down=BTN_BG_DOWN,
                       background_color=rgba(t('btn_info')))
            b.bind(on_press=lambda x, v=val: self._set(v))
            prow.add_widget(b)
        body.add_widget(prow)

        body.add_widget(Label())

        save_b = btn('Save & Send Brightness', bg=t('btn_ok'), fg='#000000', bold=True)
        save_b.bind(on_press=self._save)
        body.add_widget(save_b)

        root.add_widget(body)
        self.add_widget(root)

    def _on_slider(self, w, val):
        self.big_lbl.text = f'{int(val)}%'

    def _set(self, val):
        self.br_sl.value  = val
        self.big_lbl.text = f'{val}%'

    def _save(self, _):
        state.brightness = int(self.br_sl.value)
        from commands.led_commands import get_board
        board = get_board(state.device_ip)
        if board.connect():
            board.set_brightness(state.brightness)
            board.disconnect()
        self.manager.current = 'home'

    def on_enter(self):
        self.br_sl.value  = state.brightness
        self.big_lbl.text = f'{state.brightness}%'


# ══════════════════════════════════════════════════════
# DATE & TIME SCREEN  (rebuilt for clarity: bigger text,
# high-contrast card, seconds always visible)
# ══════════════════════════════════════════════════════

class DateTimeScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self._build()

    def _build(self):
        bg_screen(self)
        root = BoxLayout(orientation='vertical')
        root.add_widget(HeaderBar('Date & Time', self, icon_name='clock'))

        body = BoxLayout(orientation='vertical', padding=PAD, spacing=14)

        # High-contrast live clock card
        clock_card = Card(size_hint_y=None, height=150,
                           orientation='vertical', padding=CARD_PAD, spacing=2)
        self.live_lbl = Label(
            text='', font_name=FONT_TEXT, bold=True,
            font_size=XXL + 10, color=hex2rgba(t('accent')),
            size_hint_y=None, height=90,
            halign='center', valign='middle',
        )
        clock_card.add_widget(self.live_lbl)

        self.date_lbl2 = Label(
            text='', font_name=FONT_TEXT, bold=True,
            font_size=LG, color=hex2rgba(t('text')),
            size_hint_y=None, height=36,
            halign='center', valign='middle',
        )
        clock_card.add_widget(self.date_lbl2)
        body.add_widget(clock_card)

        body.add_widget(section('Show Clock on Display'))
        row = BoxLayout(size_hint_y=None, height=48, spacing=10)
        row.add_widget(Label(text='Enable Clock', font_name=FONT_TEXT, font_size=MD,
                              color=hex2rgba(t('text')),
                              halign='left', valign='middle'))
        self.clk_sw = Switch(active=state.clock_enabled,
                              size_hint=(None, None), size=(80, 40))
        row.add_widget(self.clk_sw)
        body.add_widget(row)

        body.add_widget(section('Clock Format'))
        fmt_row, self._fmt_btns = toggle_row(
            [('12-Hour', '12h'), ('24-Hour', '24h')],
            state.clock_format, self._set_fmt)
        body.add_widget(fmt_row)

        body.add_widget(Label())

        sync_b = btn('Sync Time to Board', bg=t('btn_ok'), fg='#000000', bold=True)
        sync_b.bind(on_press=self._sync)
        body.add_widget(sync_b)

        root.add_widget(body)
        self.add_widget(root)
        Clock.schedule_interval(self._tick, 1)

    def _tick(self, dt):
        now = datetime.now()
        if state.clock_format == '12h':
            self.live_lbl.text = now.strftime('%I:%M:%S %p')
        else:
            self.live_lbl.text = now.strftime('%H:%M:%S')
        self.date_lbl2.text = now.strftime('%A, %d %B %Y')

    def _set_fmt(self, fmt):
        state.clock_format = fmt
        for v, b in self._fmt_btns.items():
            b.background_color = rgba(t('accent') if v == fmt else t('btn_info'))
            b.color             = rgba('#000000' if v == fmt else '#FFFFFF')

    def _sync(self, _):
        state.clock_enabled = self.clk_sw.active
        from commands.led_commands import get_board
        board = get_board(state.device_ip)
        if board.connect():
            board.sync_time()
            board.disconnect()
        self.manager.current = 'home'


# ══════════════════════════════════════════════════════
# COLOR SCREEN
# ══════════════════════════════════════════════════════

TEXT_COLORS = [
    ('#FFD700','Gold'), ('#FF0000','Red'), ('#00FF00','Green'),
    ('#4FC3F7','Blue'), ('#FF69B4','Pink'), ('#FF8C00','Orange'),
    ('#FFFFFF','White'), ('#00FF88','Mint'), ('#DA70D6','Purple'),
    ('#7FFF00','Lime'), ('#FF4500','OranRed'), ('#00CED1','Teal'),
]
BG_COLORS = [
    ('#000000','Black'), ('#0D0D0D','DarkBG'), ('#00008B','DkBlue'),
    ('#8B0000','DkRed'), ('#006400','DkGreen'), ('#4B0082','Indigo'),
]


class ColorScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self._tc = state.text_color
        self._bc = state.bg_color
        self._build()

    def _build(self):
        bg_screen(self)
        root = BoxLayout(orientation='vertical')
        root.add_widget(HeaderBar('Text & Background Colors', self, icon_name='palette'))

        body = BoxLayout(orientation='vertical', padding=PAD, spacing=10)

        # Preview
        self.prev = Card(size_hint_y=None, height=66,
                          orientation='vertical', padding=10, spacing=2)
        self.prev_lbl = Label(
            text=state.text_content or 'Preview Text',
            font_name=FONT_TEXT, font_size=LG, color=hex2rgba(self._tc),
            halign='center', valign='middle',
        )
        self.prev_lbl.bind(size=self.prev_lbl.setter('text_size'))
        self.prev.add_widget(self.prev_lbl)
        body.add_widget(self.prev)

        body.add_widget(section('Text Color'))
        tg = GridLayout(cols=4, spacing=5, size_hint_y=None, height=150)
        for hx, name in TEXT_COLORS:
            b = Button(text=name, font_name=FONT_TEXT, font_size=XS,
                       color=rgba('#000000') if hx in ('#FFD700','#FFFFFF','#00FF00','#7FFF00','#00FF88') else rgba('#FFFFFF'),
                       background_normal=BTN_BG, background_down=BTN_BG_DOWN, background_color=rgba(hx))
            b.bind(on_press=lambda x, h=hx: self._pick_text(h))
            tg.add_widget(b)
        body.add_widget(tg)

        body.add_widget(section('Background Color'))
        bg = GridLayout(cols=3, spacing=5, size_hint_y=None, height=100)
        for hx, name in BG_COLORS:
            b = Button(text=name, font_name=FONT_TEXT, font_size=XS, color=rgba('#FFFFFF'),
                       background_normal=BTN_BG, background_down=BTN_BG_DOWN, background_color=rgba(hx))
            b.bind(on_press=lambda x, h=hx: self._pick_bg(h))
            bg.add_widget(b)
        body.add_widget(bg)

        body.add_widget(Label())
        save_b = btn('Save Colors', bg=t('btn_ok'), fg='#000000', bold=True)
        save_b.bind(on_press=self._save)
        body.add_widget(save_b)
        root.add_widget(body)
        self.add_widget(root)

    def _pick_text(self, h):
        self._tc = h
        self.prev_lbl.color = hex2rgba(h)

    def _pick_bg(self, h):
        self._bc = h

    def _save(self, _):
        state.text_color = self._tc
        state.bg_color   = self._bc
        self.manager.current = 'home'

    def on_enter(self):
        self._tc = state.text_color
        self._bc = state.bg_color
        self.prev_lbl.text  = state.text_content or 'Preview'
        self.prev_lbl.color = hex2rgba(self._tc)


# ══════════════════════════════════════════════════════
# SCROLL SCREEN
# ══════════════════════════════════════════════════════

DIRECTIONS = [('Left','left'),('Right','right'),
              ('Up','up'),('Down','down'),
              ('Static','none'),('Bounce','bounce')]
EFFECTS    = [('Normal','normal'),('Blink','blink'),
              ('Fade In','fade_in'),('Gradient','gradient'),
              ('Sparkle','sparkle'),('Wave','wave')]


class ScrollScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self._dir = state.scroll_direction
        self._eff = state.scroll_effect
        self._build()

    def _build(self):
        bg_screen(self)
        root = BoxLayout(orientation='vertical')
        root.add_widget(HeaderBar('Scroll Settings', self, icon_name='scroll'))
        body = BoxLayout(orientation='vertical', padding=PAD, spacing=12)

        body.add_widget(section('Scroll Speed'))
        sr = BoxLayout(size_hint_y=None, height=48, spacing=10)
        self.sp_lbl = Label(text=str(state.scroll_speed), font_name=FONT_TEXT, bold=True,
                             font_size=XL, color=hex2rgba(t('accent')), size_hint_x=0.15)
        self.sp_sl = Slider(min=1, max=10, value=state.scroll_speed,
                             step=1, size_hint_x=0.85)
        self.sp_sl.bind(value=lambda w, v: setattr(self.sp_lbl, 'text', str(int(v))))
        sr.add_widget(self.sp_lbl); sr.add_widget(self.sp_sl)
        body.add_widget(sr)

        body.add_widget(section('Direction'))
        dg = GridLayout(cols=3, spacing=6, size_hint_y=None, height=110)
        self.d_btns = {}
        for lab, val in DIRECTIONS:
            b = Button(text=lab, font_name=FONT_TEXT, font_size=SM, color=rgba('#FFFFFF'),
                       background_normal=BTN_BG, background_down=BTN_BG_DOWN,
                       background_color=rgba(t('accent') if val==self._dir else t('btn_info')))
            b.bind(on_press=lambda x, v=val: self._pick_dir(v))
            self.d_btns[val] = b
            dg.add_widget(b)
        body.add_widget(dg)

        body.add_widget(section('Text Effect'))
        eg = GridLayout(cols=3, spacing=6, size_hint_y=None, height=110)
        self.e_btns = {}
        for lab, val in EFFECTS:
            b = Button(text=lab, font_name=FONT_TEXT, font_size=SM, color=rgba('#FFFFFF'),
                       background_normal=BTN_BG, background_down=BTN_BG_DOWN,
                       background_color=rgba(t('accent') if val==self._eff else t('btn_info')))
            b.bind(on_press=lambda x, v=val: self._pick_eff(v))
            self.e_btns[val] = b
            eg.add_widget(b)
        body.add_widget(eg)

        body.add_widget(Label())
        save_b = btn('Save Scroll Settings', bg=t('btn_ok'), fg='#000000', bold=True)
        save_b.bind(on_press=self._save)
        body.add_widget(save_b)
        root.add_widget(body)
        self.add_widget(root)

    def _pick_dir(self, val):
        for v, b in self.d_btns.items():
            b.background_color = rgba(t('accent') if v==val else t('btn_info'))
        self._dir = val

    def _pick_eff(self, val):
        for v, b in self.e_btns.items():
            b.background_color = rgba(t('accent') if v==val else t('btn_info'))
        self._eff = val

    def _save(self, _):
        state.scroll_speed     = int(self.sp_sl.value)
        state.scroll_direction = self._dir
        state.scroll_effect    = self._eff
        self.manager.current = 'home'

    def on_enter(self):
        self.sp_sl.value = state.scroll_speed
        self._pick_dir(state.scroll_direction)
        self._pick_eff(state.scroll_effect)


# ══════════════════════════════════════════════════════
# DEVICE / CONNECT SCREEN
# ══════════════════════════════════════════════════════

class DeviceScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self._build()

    def _build(self):
        bg_screen(self)
        root = BoxLayout(orientation='vertical')
        root.add_widget(HeaderBar('Connect Board', self, icon_name='wifi'))
        body = BoxLayout(orientation='vertical', padding=PAD, spacing=12)

        ip_card = Card(size_hint_y=None, height=134,
                        orientation='vertical', padding=CARD_PAD, spacing=8)
        ip_card.add_widget(Label(text='Board IP Address', font_name=FONT_TEXT, font_size=SM,
                                  color=hex2rgba(t('sub')), size_hint_y=None,
                                  height=22, halign='left', valign='middle'))
        self.ip_in = TextInput(
            text=state.device_ip, font_name=FONT_TEXT, font_size=MD, multiline=False,
            size_hint_y=None, height=46,
            background_color=rgba(t('input_bg')),
            foreground_color=rgba(t('text')),
            cursor_color=rgba(t('accent')),
        )
        con_b = btn('Connect Manually', bg=t('btn_info'), fg='#FFFFFF',
                    height=42, fs=SM, bold=True)
        con_b.bind(on_press=self._manual)
        ip_card.add_widget(self.ip_in)
        ip_card.add_widget(con_b)
        body.add_widget(ip_card)

        scan_b = btn('Auto Scan WiFi Network', bg=t('btn_ok'), fg='#000000', bold=True)
        scan_b.bind(on_press=self._scan)
        body.add_widget(scan_b)

        self.st_lbl = Label(text='Tap Scan to find boards on WiFi',
                             font_name=FONT_TEXT, font_size=SM, color=hex2rgba(t('sub')),
                             size_hint_y=None, height=30,
                             halign='center', valign='middle')
        self.st_lbl.bind(size=self.st_lbl.setter('text_size'))
        body.add_widget(self.st_lbl)

        self.res_box = BoxLayout(orientation='vertical', spacing=8,
                                  size_hint_y=None)
        self.res_box.bind(minimum_height=self.res_box.setter('height'))
        body.add_widget(self.res_box)
        body.add_widget(Label())
        root.add_widget(body)
        self.add_widget(root)

    def _scan(self, _):
        self.st_lbl.text  = 'Scanning...'
        self.st_lbl.color = hex2rgba(t('accent'))
        self.res_box.clear_widgets()
        from commands.led_commands import USE_MOCK
        if USE_MOCK:
            Clock.schedule_once(lambda dt: self._show([
                {'ip':'192.168.1.100','name':'WF2-Board-Hotel'},
                {'ip':'192.168.1.101','name':'WF2-Board-2'},
            ]), 1.5)
        else:
            from commands.led_commands import discover_boards
            threading.Thread(
                target=lambda: Clock.schedule_once(
                    lambda dt: self._show(discover_boards()), 0),
                daemon=True).start()

    def _show(self, boards):
        self.res_box.clear_widgets()
        if not boards:
            self.st_lbl.text  = 'No boards found'
            self.st_lbl.color = hex2rgba(t('btn_del'))
            return
        self.st_lbl.text  = f'Found {len(boards)} board(s)'
        self.st_lbl.color = hex2rgba(t('ok'))
        for b in boards:
            row = Card(size_hint_y=None, height=58,
                        orientation='horizontal',
                        padding=[CARD_PAD, 0], spacing=8)
            info = BoxLayout(orientation='vertical')
            n = Label(text=b["name"], font_name=FONT_TEXT, bold=True, font_size=MD,
                      color=hex2rgba(t('text')), halign='left', valign='middle')
            n.bind(size=n.setter('text_size'))
            ip = Label(text=b['ip'], font_name=FONT_TEXT, font_size=XS, color=hex2rgba(t('sub')),
                       halign='left', valign='middle')
            ip.bind(size=ip.setter('text_size'))
            info.add_widget(n); info.add_widget(ip)
            sel = Button(text='Select', font_name=FONT_TEXT, bold=True,
                         size_hint=(None,None), size=(80,38),
                         font_size=SM, color=rgba('#000000'),
                         background_normal=BTN_BG, background_down=BTN_BG_DOWN, background_color=rgba('#00E676'))
            sel.bind(on_press=lambda x, bd=b: self._select(bd))
            row.add_widget(info); row.add_widget(sel)
            self.res_box.add_widget(row)

    def _manual(self, _):
        self._select({'ip': self.ip_in.text.strip(),
                      'name': f'Board-{self.ip_in.text.strip()}'})

    def _select(self, board):
        state.device_ip    = board['ip']
        state.device_name  = board['name']
        state.is_connected = True
        state.save()
        self.manager.current = 'home'


# ══════════════════════════════════════════════════════
# PROGRAM EDITOR SCREEN
# (LEDArt-style single-program editor: text + font controls +
#  animation + speed/hold + border/background/canvas rotation)
# ══════════════════════════════════════════════════════

FONT_CHOICES = ['Arial', 'Roboto', 'DejaVu Sans', 'Times New Roman', 'Courier New']
ANIM_EFFECTS = ['Display static', 'Scroll left', 'Scroll right', 'Scroll up',
                 'Scroll down', 'Blink', 'Fade in', 'Snow', 'Curtain']
ALIGN_OPTS   = [('Left', 'left'), ('Center', 'center'), ('Right', 'right')]
ROTATIONS    = ['Normal', '90°', '180°', '270°']
HOLD_OPTS    = [1, 2, 3, 5, 8, 10]


class ProgramEditorScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self._align      = state.text_align
        self._rotation   = state.canvas_rotation
        self._hold       = state.hold_seconds
        self._build()

    def _build(self):
        bg_screen(self)
        root = BoxLayout(orientation='vertical')
        root.add_widget(HeaderBar('Program Editor', self, icon_name='program'))

        sv = ScrollView()
        body = BoxLayout(orientation='vertical', padding=PAD, spacing=14,
                          size_hint_y=None)
        body.bind(minimum_height=body.setter('height'))

        # Preview box, like the LED panel preview in the reference app
        self.preview = Card(size_hint_y=None, height=90,
                             orientation='vertical', padding=10)
        self.preview_lbl = Label(
            text=state.text_content, font_name=FONT_TEXT, bold=state.font_bold,
            italic=state.font_italic, font_size=LG, color=hex2rgba(state.text_color),
            halign=self._align, valign='middle',
        )
        self.preview_lbl.bind(size=self.preview_lbl.setter('text_size'))
        self.preview.add_widget(self.preview_lbl)
        body.add_widget(self.preview)

        # Text
        body.add_widget(section('Program Text'))
        self.txt = TextInput(
            text=state.text_content, multiline=True,
            font_name=FONT_TEXT, font_size=MD,
            size_hint_y=None, height=90,
            background_color=rgba(t('input_bg')),
            foreground_color=rgba(t('text')),
            cursor_color=rgba(t('accent')),
        )
        self.txt.bind(text=self._update_preview)
        body.add_widget(self.txt)

        # Font family + size
        body.add_widget(section('Font'))
        frow = BoxLayout(size_hint_y=None, height=46, spacing=8)
        self.font_spin = Spinner(
            text=state.font_name, values=FONT_CHOICES,
            font_name=FONT_TEXT, font_size=SM,
            background_color=rgba(t('btn_info')), color=rgba('#FFFFFF'),
            size_hint_x=0.55,
        )
        self.size_spin = Spinner(
            text=str(state.text_size), values=[str(v) for v in range(10, 49, 2)],
            font_name=FONT_TEXT, font_size=SM,
            background_color=rgba(t('btn_info')), color=rgba('#FFFFFF'),
            size_hint_x=0.2,
        )
        self.color_btn = Button(
            text='Color', font_name=FONT_TEXT, bold=True, font_size=SM,
            size_hint_x=0.25,
            color=rgba('#000000'), background_normal=BTN_BG, background_down=BTN_BG_DOWN,
            background_color=rgba(state.text_color),
        )
        self.color_btn.bind(on_press=self._cycle_color)
        frow.add_widget(self.font_spin)
        frow.add_widget(self.size_spin)
        frow.add_widget(self.color_btn)
        body.add_widget(frow)

        # Bold / Italic / Underline + Alignment
        style_row = BoxLayout(size_hint_y=None, height=44, spacing=6)
        self.bold_btn = self._style_toggle('B', state.font_bold)
        self.ital_btn = self._style_toggle('I', state.font_italic)
        self.und_btn  = self._style_toggle('U', state.font_underline)
        self.bold_btn.bind(on_press=lambda x: self._toggle_style('bold'))
        self.ital_btn.bind(on_press=lambda x: self._toggle_style('italic'))
        self.und_btn.bind(on_press=lambda x: self._toggle_style('underline'))
        style_row.add_widget(self.bold_btn)
        style_row.add_widget(self.ital_btn)
        style_row.add_widget(self.und_btn)

        align_row, self._align_btns = toggle_row(
            ALIGN_OPTS, self._align, self._pick_align)
        body.add_widget(style_row)
        body.add_widget(align_row)

        # Animation effect
        body.add_widget(section('Animation Effect'))
        self.anim_spin = Spinner(
            text=state.anim_effect, values=ANIM_EFFECTS,
            font_name=FONT_TEXT, font_size=SM, size_hint_y=None, height=44,
            background_color=rgba(t('btn_info')), color=rgba('#FFFFFF'),
        )
        body.add_widget(self.anim_spin)

        # Speed
        body.add_widget(section('Speed'))
        srow = BoxLayout(size_hint_y=None, height=44, spacing=10)
        self.speed_lbl = Label(text=str(state.scroll_speed), font_name=FONT_TEXT,
                                bold=True, font_size=LG, color=hex2rgba(t('accent')),
                                size_hint_x=0.15)
        self.speed_sl = Slider(min=1, max=10, step=1, value=state.scroll_speed,
                                size_hint_x=0.85)
        self.speed_sl.bind(value=lambda w, v: setattr(self.speed_lbl, 'text', str(int(v))))
        srow.add_widget(self.speed_lbl); srow.add_widget(self.speed_sl)
        body.add_widget(srow)

        # Hold time
        body.add_widget(section('Hold (seconds before repeat)'))
        hrow = BoxLayout(size_hint_y=None, height=44, spacing=6)
        self._hold_btns = {}
        for sec in HOLD_OPTS:
            b = Button(text=f'{sec}s', font_name=FONT_TEXT, font_size=SM,
                       color=rgba('#000000' if sec == self._hold else '#FFFFFF'),
                       background_normal=BTN_BG, background_down=BTN_BG_DOWN,
                       background_color=rgba(t('accent') if sec == self._hold else t('btn_info')))
            b.bind(on_press=lambda x, s=sec: self._pick_hold(s))
            self._hold_btns[sec] = b
            hrow.add_widget(b)
        body.add_widget(hrow)

        # Immediate clear
        crow = BoxLayout(size_hint_y=None, height=46, spacing=10)
        crow.add_widget(Label(text='Immediate Clear', font_name=FONT_TEXT, font_size=MD,
                               color=hex2rgba(t('text')), halign='left', valign='middle'))
        self.clear_sw = Switch(active=state.immediate_clear,
                                size_hint=(None, None), size=(80, 40))
        crow.add_widget(self.clear_sw)
        body.add_widget(crow)

        # Border
        body.add_widget(section('Border'))
        brow = BoxLayout(size_hint_y=None, height=46, spacing=10)
        brow.add_widget(Label(text='Enable Border', font_name=FONT_TEXT, font_size=MD,
                               color=hex2rgba(t('text')), halign='left', valign='middle'))
        self.border_sw = Switch(active=state.border_enabled,
                                 size_hint=(None, None), size=(80, 40))
        brow.add_widget(self.border_sw)
        body.add_widget(brow)

        # Canvas rotation
        body.add_widget(section('Canvas Rotation'))
        rot_row, self._rot_btns = toggle_row(
            [(r, r) for r in ROTATIONS], self._rotation, self._pick_rotation)
        body.add_widget(rot_row)

        body.add_widget(Label(size_hint_y=None, height=10))
        save_b = btn('Save Program', bg=t('btn_ok'), fg='#000000', bold=True)
        save_b.bind(on_press=self._save)
        body.add_widget(save_b)

        body.add_widget(Label(size_hint_y=None, height=20))
        sv.add_widget(body)
        root.add_widget(sv)
        self.add_widget(root)

    def _style_toggle(self, label, active):
        b = Button(
            text=label, font_name=FONT_TEXT, bold=True, font_size=MD,
            color=rgba('#000000' if active else '#FFFFFF'),
            background_normal=BTN_BG, background_down=BTN_BG_DOWN,
            background_color=rgba(t('accent') if active else t('btn_info')),
        )
        return b

    def _toggle_style(self, which):
        attr = {'bold': 'font_bold', 'italic': 'font_italic', 'underline': 'font_underline'}[which]
        btn_map = {'bold': self.bold_btn, 'italic': self.ital_btn, 'underline': self.und_btn}
        setattr(state, attr, not getattr(state, attr))
        active = getattr(state, attr)
        b = btn_map[which]
        b.background_color = rgba(t('accent') if active else t('btn_info'))
        b.color             = rgba('#000000' if active else '#FFFFFF')
        self._update_preview()

    def _pick_align(self, val):
        self._align = val
        for v, b in self._align_btns.items():
            b.background_color = rgba(t('accent') if v == val else t('btn_info'))
            b.color             = rgba('#000000' if v == val else '#FFFFFF')
        self.preview_lbl.halign = val

    def _pick_hold(self, sec):
        self._hold = sec
        for v, b in self._hold_btns.items():
            b.background_color = rgba(t('accent') if v == sec else t('btn_info'))
            b.color             = rgba('#000000' if v == sec else '#FFFFFF')

    def _pick_rotation(self, val):
        self._rotation = val
        for v, b in self._rot_btns.items():
            b.background_color = rgba(t('accent') if v == val else t('btn_info'))
            b.color             = rgba('#000000' if v == val else '#FFFFFF')

    def _cycle_color(self, _):
        colors = [c for c, _n in TEXT_COLORS]
        cur = state.text_color
        idx = colors.index(cur) if cur in colors else -1
        new = colors[(idx + 1) % len(colors)]
        state.text_color = new
        self.color_btn.background_color = rgba(new)
        self.preview_lbl.color = rgba(new)

    def _update_preview(self, *a):
        self.preview_lbl.text = self.txt.text or 'Preview'
        self.preview_lbl.bold = state.font_bold
        self.preview_lbl.italic = state.font_italic
        self.preview_lbl.underline = state.font_underline

    def _save(self, _):
        state.text_content    = self.txt.text.strip() or state.text_content
        state.font_name        = self.font_spin.text
        state.text_size        = int(self.size_spin.text)
        state.anim_effect      = self.anim_spin.text
        state.scroll_speed     = int(self.speed_sl.value)
        state.hold_seconds     = self._hold
        state.immediate_clear  = self.clear_sw.active
        state.border_enabled   = self.border_sw.active
        state.text_align       = self._align
        state.canvas_rotation  = self._rotation
        state.save()
        self.manager.current = 'home'

    def on_enter(self):
        self.txt.text = state.text_content
        self._update_preview()


# ══════════════════════════════════════════════════════
# TUTORIAL SCREEN
# ══════════════════════════════════════════════════════

STEPS = [
    ('1', 'Connect Board', 'wifi',
     'Go to "Connect" -> Enter board IP (e.g. 192.168.1.100) or tap Auto Scan. '
     'Board and phone must be on same WiFi network.'),
    ('2', 'Add Menu Items', 'menu_items',
     'Go to "Menu Items" -> Tap + Add Item -> Enter name, price, category and color. '
     'You can add unlimited items.'),
    ('3', 'Set Display Message', 'display',
     'Go to "Display" -> Type your custom message or pick a quick message. '
     'Set font size as needed.'),
    ('4', 'Choose Colors', 'palette',
     'Go to "Colors" -> Pick text color (Gold, Red, Green...) and background color (Black recommended for LED).'),
    ('5', 'Set Scroll', 'scroll',
     'Go to "Scroll" -> Choose direction (Left is most common), speed (1-10) and effect (Normal, Blink, Wave...).'),
    ('6', 'Set Brightness', 'brightness',
     'Go to "Brightness" -> Adjust slider 0-100%. '
     'Normal indoor use: 70-80%. Night: 20-40%.'),
    ('7', 'Sync Time', 'clock',
     'Go to "Date & Time" -> Enable clock on display if needed, choose 12h/24h and tap Sync.'),
    ('8', 'Send to Board', 'send',
     'From Home screen -> Tap SEND TO BOARD. '
     'Or from Menu Items -> tap the send icon next to any item to send that item\'s name and price directly.'),
    ('9', 'Settings', 'settings',
     'Change app theme (Dark/Blue/Purple/Green/Light), language (English/Tamil), '
     'export or import your data as a backup .txt file, and manage your account.'),
]


class TutorialScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self._build()

    def _build(self):
        bg_screen(self)
        root = BoxLayout(orientation='vertical')
        root.add_widget(HeaderBar('How to Use', self, icon_name='help'))

        sv = ScrollView()
        body = BoxLayout(orientation='vertical', padding=PAD, spacing=10,
                          size_hint_y=None)
        body.bind(minimum_height=body.setter('height'))

        title = Label(
            text="BRO'S LED Controller — User Guide",
            font_name=FONT_TEXT, bold=True, font_size=LG, color=hex2rgba(t('accent')),
            size_hint_y=None, height=40,
            halign='center', valign='middle',
        )
        title.bind(size=title.setter('text_size'))
        body.add_widget(title)

        for num, heading, icon_name, desc in STEPS:
            card = Card(size_hint_y=None, height=130,
                         orientation='vertical', padding=CARD_PAD, spacing=6)
            h_row = BoxLayout(size_hint_y=None, height=32, spacing=8)
            num_lbl = Label(
                text=num, font_name=FONT_TEXT, bold=True, font_size=MD,
                size_hint=(None, None), size=(24, 28),
                color=hex2rgba(t('accent')),
            )
            ic_lbl = Label(
                text=icon(icon_name), font_name=FONT_ICON, font_size=MD,
                size_hint=(None, None), size=(24, 28),
                color=hex2rgba(t('accent2')),
            )
            h_lbl = Label(
                text=heading, font_name=FONT_TEXT, bold=True, font_size=MD,
                color=hex2rgba(t('text')), halign='left', valign='middle',
            )
            h_lbl.bind(size=h_lbl.setter('text_size'))
            h_row.add_widget(num_lbl)
            h_row.add_widget(ic_lbl)
            h_row.add_widget(h_lbl)
            card.add_widget(h_row)

            d_lbl = Label(
                text=desc, font_name=FONT_TEXT, font_size=SM,
                color=hex2rgba(t('sub')),
                halign='left', valign='top',
                text_size=(None, None),
            )
            d_lbl.bind(size=lambda w, v: setattr(w, 'text_size', (v[0], None)))
            card.add_widget(d_lbl)
            body.add_widget(card)

        body.add_widget(Label(size_hint_y=None, height=20))
        sv.add_widget(body)
        root.add_widget(sv)
        self.add_widget(root)


# ══════════════════════════════════════════════════════
# SETTINGS SCREEN
# ══════════════════════════════════════════════════════

THEMES_LIST = [('Dark', 'dark'), ('Blue', 'blue'),
               ('Purple', 'purple'), ('Green', 'green'),
               ('Light', 'light')]


class _FileSavePopup(Popup):
    """Simple save-as dialog for export."""
    def __init__(self, on_confirm, default_name='bros_led_backup.txt', **kw):
        kw['title'] = 'Export — choose a location'
        kw['size_hint'] = (0.95, 0.9)
        super().__init__(**kw)
        self._on_confirm = on_confirm

        root = BoxLayout(orientation='vertical', padding=10, spacing=8)
        start_path = os.path.expanduser('~')
        self.chooser = FileChooserListView(path=start_path, dirselect=True)
        root.add_widget(self.chooser)

        name_row = BoxLayout(size_hint_y=None, height=44, spacing=6)
        name_row.add_widget(Label(text='File name:', font_name=FONT_TEXT,
                                   size_hint_x=0.3))
        self.name_in = TextInput(text=default_name, multiline=False,
                                  font_name=FONT_TEXT, font_size=SM)
        name_row.add_widget(self.name_in)
        root.add_widget(name_row)

        btn_row = BoxLayout(size_hint_y=None, height=48, spacing=10)
        cancel_b = Button(text='Cancel', font_name=FONT_TEXT, bold=True,
                           background_normal=BTN_BG, background_down=BTN_BG_DOWN, background_color=rgba('#37474F'))
        cancel_b.bind(on_press=lambda x: self.dismiss())
        save_b = Button(text='Export', font_name=FONT_TEXT, bold=True,
                         color=rgba('#000000'),
                         background_normal=BTN_BG, background_down=BTN_BG_DOWN, background_color=rgba(t('btn_ok')))
        save_b.bind(on_press=self._confirm)
        btn_row.add_widget(cancel_b)
        btn_row.add_widget(save_b)
        root.add_widget(btn_row)

        self.content = root

    def _confirm(self, _):
        folder = self.chooser.path
        name = self.name_in.text.strip() or 'bros_led_backup.txt'
        if not name.lower().endswith('.txt'):
            name += '.txt'
        full_path = os.path.join(folder, name)
        self.dismiss()
        self._on_confirm(full_path)


class _FileOpenPopup(Popup):
    """Simple open dialog for import, filtered to .txt files."""
    def __init__(self, on_confirm, **kw):
        kw['title'] = 'Import — select a .txt backup file'
        kw['size_hint'] = (0.95, 0.9)
        super().__init__(**kw)
        self._on_confirm = on_confirm

        root = BoxLayout(orientation='vertical', padding=10, spacing=8)
        start_path = os.path.expanduser('~')
        self.chooser = FileChooserListView(path=start_path, filters=['*.txt'])
        root.add_widget(self.chooser)

        btn_row = BoxLayout(size_hint_y=None, height=48, spacing=10)
        cancel_b = Button(text='Cancel', font_name=FONT_TEXT, bold=True,
                           background_normal=BTN_BG, background_down=BTN_BG_DOWN, background_color=rgba('#37474F'))
        cancel_b.bind(on_press=lambda x: self.dismiss())
        open_b = Button(text='Import', font_name=FONT_TEXT, bold=True,
                         color=rgba('#000000'),
                         background_normal=BTN_BG, background_down=BTN_BG_DOWN, background_color=rgba(t('btn_ok')))
        open_b.bind(on_press=self._confirm)
        btn_row.add_widget(cancel_b)
        btn_row.add_widget(open_b)
        root.add_widget(btn_row)

        self.content = root

    def _confirm(self, _):
        sel = self.chooser.selection
        if not sel:
            return
        path = sel[0]
        self.dismiss()
        self._on_confirm(path)


class SettingsScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self._build()

    def _build(self):
        bg_screen(self)
        root = BoxLayout(orientation='vertical')
        root.add_widget(HeaderBar('Settings', self, icon_name='settings'))

        sv = ScrollView()
        body = BoxLayout(orientation='vertical', padding=PAD, spacing=10,
                          size_hint_y=None)
        body.bind(minimum_height=body.setter('height'))

        # Theme
        body.add_widget(section('App Theme'))
        tg = GridLayout(cols=2, spacing=8, size_hint_y=None, height=130)
        self._theme_btns = {}
        for lab, val in THEMES_LIST:
            b = Button(
                text=lab, font_name=FONT_TEXT, bold=True, font_size=SM,
                color=rgba('#FFFFFF' if val != state.theme else '#000000'),
                background_normal=BTN_BG, background_down=BTN_BG_DOWN,
                background_color=rgba(t('accent') if val == state.theme else t('btn_info')),
            )
            b.bind(on_press=lambda x, v=val: self._pick_theme(v))
            self._theme_btns[val] = b
            tg.add_widget(b)
        body.add_widget(tg)

        # Language
        body.add_widget(section('Language'))
        lr = BoxLayout(size_hint_y=None, height=52, spacing=8)
        self.en_btn = Button(
            text='English', font_name=FONT_TEXT, bold=True, font_size=SM,
            color=rgba('#000000' if state.language=='en' else '#FFFFFF'),
            background_normal=BTN_BG, background_down=BTN_BG_DOWN,
            background_color=rgba(t('accent') if state.language=='en' else t('btn_info')),
        )
        self.ta_btn = Button(
            text='Tamil', font_name=FONT_TEXT, bold=True, font_size=SM,
            color=rgba('#000000' if state.language=='ta' else '#FFFFFF'),
            background_normal=BTN_BG, background_down=BTN_BG_DOWN,
            background_color=rgba(t('accent') if state.language=='ta' else t('btn_info')),
        )
        self.en_btn.bind(on_press=lambda x: self._set_lang('en'))
        self.ta_btn.bind(on_press=lambda x: self._set_lang('ta'))
        lr.add_widget(self.en_btn); lr.add_widget(self.ta_btn)
        body.add_widget(lr)

        # Backup — Import / Export as .txt
        body.add_widget(section('Backup (Import / Export .txt)'))
        self.backup_status = Label(
            text='Export saves all your settings & menu items to a .txt file. '
                 'Import restores from a previously exported file.',
            font_name=FONT_TEXT, font_size=XS, color=hex2rgba(t('sub')),
            size_hint_y=None, height=50,
            halign='left', valign='top', text_size=(None, None),
        )
        self.backup_status.bind(size=lambda w, v: setattr(w, 'text_size', (v[0], None)))
        body.add_widget(self.backup_status)

        backup_row = BoxLayout(size_hint_y=None, height=48, spacing=8)
        export_b = btn(f'{icon("export")} Export', bg=t('btn_info'), fg='#FFFFFF',
                       height=48, fs=SM, bold=True)
        export_b.font_name = FONT_ICON
        export_b.bind(on_press=self._open_export)
        import_b = btn(f'{icon("import")} Import', bg=t('btn_info'), fg='#FFFFFF',
                       height=48, fs=SM, bold=True)
        import_b.font_name = FONT_ICON
        import_b.bind(on_press=self._open_import)
        backup_row.add_widget(export_b)
        backup_row.add_widget(import_b)
        body.add_widget(backup_row)

        # Account info
        body.add_widget(section('Account'))
        acct_card = Card(size_hint_y=None, height=64,
                          orientation='vertical', padding=CARD_PAD, spacing=4)
        self.acct_lbl = Label(
            text=f'Logged in as: {state.username}',
            font_name=FONT_TEXT, bold=True, font_size=MD, color=hex2rgba(t('text')),
            halign='left', valign='middle',
        )
        self.acct_lbl.bind(size=self.acct_lbl.setter('text_size'))
        acct_card.add_widget(self.acct_lbl)
        body.add_widget(acct_card)

        logout_b = btn('Logout', bg=t('btn_del'), fg='#FFFFFF', bold=True)
        logout_b.bind(on_press=self._logout)
        body.add_widget(logout_b)

        # About
        body.add_widget(section('About'))
        about_card = Card(size_hint_y=None, height=90,
                           orientation='vertical', padding=CARD_PAD, spacing=4)
        for txt in ["BRO'S Engineering Solution Pvt.Ltd.",
                    'LED Controller v1.0',
                    'Three Friends. One Vision. Endless Innovation.']:
            l = Label(text=txt, font_name=FONT_TEXT, font_size=XS, color=hex2rgba(t('sub')),
                      halign='left', valign='middle', size_hint_y=None, height=24)
            l.bind(size=l.setter('text_size'))
            about_card.add_widget(l)
        body.add_widget(about_card)

        save_b = btn('Save Settings', bg=t('btn_ok'), fg='#000000', bold=True)
        save_b.bind(on_press=self._save)
        body.add_widget(save_b)

        body.add_widget(Label(size_hint_y=None, height=20))
        sv.add_widget(body)
        root.add_widget(sv)
        self.add_widget(root)

    def _pick_theme(self, val):
        """User tapped a theme: save it and re-skin EVERY page live."""
        state.theme = val
        state.save()
        from kivy.app import App
        Clock.schedule_once(lambda dt: App.get_running_app().apply_theme(), 0)

    def _set_theme(self, val):
        state.theme = val
        for v, b in self._theme_btns.items():
            b.background_color = rgba(t('accent') if v==val else t('btn_info'))
            b.color            = rgba('#000000' if v==val else '#FFFFFF')

    def _set_lang(self, lang):
        state.language = lang
        self.en_btn.background_color = rgba(t('accent') if lang=='en' else t('btn_info'))
        self.en_btn.color            = rgba('#000000' if lang=='en' else '#FFFFFF')
        self.ta_btn.background_color = rgba(t('accent') if lang=='ta' else t('btn_info'))
        self.ta_btn.color            = rgba('#000000' if lang=='ta' else '#FFFFFF')

    def _open_export(self, _):
        popup = _FileSavePopup(self._do_export)
        popup.open()

    def _do_export(self, path):
        try:
            state.export_to_txt(path)
            self.backup_status.text = f'Exported successfully to:\n{path}'
            self.backup_status.color = hex2rgba(t('ok'))
        except Exception as e:
            self.backup_status.text = f'Export failed: {e}'
            self.backup_status.color = hex2rgba(t('btn_del'))

    def _open_import(self, _):
        popup = _FileOpenPopup(self._do_import)
        popup.open()

    def _do_import(self, path):
        try:
            state.import_from_txt(path)
            self.backup_status.text = f'Imported successfully from:\n{path}'
            self.backup_status.color = hex2rgba(t('ok'))
            self._refresh_from_state()
            from kivy.app import App
            Clock.schedule_once(lambda dt: App.get_running_app().apply_theme(), 0)
        except Exception as e:
            self.backup_status.text = f'Import failed: {e}'
            self.backup_status.color = hex2rgba(t('btn_del'))

    def _refresh_from_state(self):
        self._set_theme(state.theme)
        self._set_lang(state.language)
        self.acct_lbl.text = f'Logged in as: {state.username}'

    def _save(self, _):
        state.save()
        self.manager.current = 'home'

    def _logout(self, _):
        state.logged_in = False
        state.username  = ''
        self.manager.current = 'login'

    def on_enter(self):
        self.acct_lbl.text = f'Logged in as: {state.username}'
