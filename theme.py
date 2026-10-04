"""Theme Engine — Dark / Light modes + 3 colour themes (Blue, Purple, Green)"""
import os

THEMES = {
    'dark': {
        'label':    'Dark',
        'bg':       (0.05, 0.05, 0.12, 1),
        'card':     '#0F1A2E',
        'header':   '#080D1A',
        'accent':   '#FFD700',
        'accent2':  '#4FC3F7',
        'btn_ok':   '#FFD700',
        'btn_del':  '#E53935',
        'btn_info': '#1565C0',
        'text':     '#FFFFFF',
        'sub':      '#B0B6C3',
        'input_bg': '#111927',
        'ok':       '#00E676',
        'is_dark':  True,
    },
    'blue': {
        'label':    'Blue',
        'bg':       (0.02, 0.1, 0.22, 1),
        'card':     '#0A1F3D',
        'header':   '#051229',
        'accent':   '#4FC3F7',
        'accent2':  '#FFD700',
        'btn_ok':   '#0288D1',
        'btn_del':  '#E53935',
        'btn_info': '#01579B',
        'text':     '#FFFFFF',
        'sub':      '#BBE0FB',
        'input_bg': '#0D2847',
        'ok':       '#00E676',
        'is_dark':  True,
    },
    'purple': {
        'label':    'Purple',
        'bg':       (0.08, 0.02, 0.18, 1),
        'card':     '#1A0533',
        'header':   '#0D0020',
        'accent':   '#CE93D8',
        'accent2':  '#FFD700',
        'btn_ok':   '#8E24AA',
        'btn_del':  '#E53935',
        'btn_info': '#4A148C',
        'text':     '#FFFFFF',
        'sub':      '#DFBEE6',
        'input_bg': '#230A40',
        'ok':       '#00E676',
        'is_dark':  True,
    },
    'green': {
        'label':    'Green',
        'bg':       (0.02, 0.12, 0.05, 1),
        'card':     '#0A2010',
        'header':   '#051208',
        'accent':   '#00E676',
        'accent2':  '#FFD700',
        'btn_ok':   '#2E7D32',
        'btn_del':  '#E53935',
        'btn_info': '#1B5E20',
        'text':     '#FFFFFF',
        'sub':      '#C2E8C5',
        'input_bg': '#0E2A15',
        'ok':       '#00E676',
        'is_dark':  True,
    },
    'light': {
        'label':    'Light',
        'bg':       (0.94, 0.95, 0.97, 1),
        'card':     '#FFFFFF',
        'header':   '#E9ECF3',
        'accent':   '#A66300',
        'accent2':  '#0277BD',
        'btn_ok':   '#D4A017',
        'btn_del':  '#D32F2F',
        'btn_info': '#1565C0',
        'text':     '#1A1A1A',
        'sub':      '#5A5F6B',
        'input_bg': '#EEF0F4',
        'ok':       '#1B7F3B',
        'is_dark':  False,
    },
}

# ── Fonts ────────────────────────────────────────────────
# Kivy's default UI font ('Roboto') is missing almost every symbol/
# icon glyph this app needs, which is why icon-only buttons were all
# rendering as the same blank box on real devices. DejaVuSans (also
# bundled with Kivy, no extra assets required) covers the safe icon
# set used throughout the app. Plain text uses the regular (non-bold)
# weight by default; bold is reserved for headings/emphasis only.
FONT_TEXT  = 'Roboto'        # body text / labels
FONT_ICON  = 'DejaVuSans'    # icon glyphs (see utils/icons.py)

# Font sizes
XXL  = 32
XL   = 26
LG   = 20
MD   = 16
SM   = 13
XS   = 11

# Layout
PAD       = 16
CARD_PAD  = 14
BTN_H     = 52
RADIUS    = 14


def t(key):
    from utils.app_state import state
    return THEMES.get(state.theme, THEMES['dark'])[key]


def is_dark_theme():
    from utils.app_state import state
    return THEMES.get(state.theme, THEMES['dark']).get('is_dark', True)


def hex2rgba(h):
    from kivy.utils import get_color_from_hex
    return get_color_from_hex(h)


# ── Rounded button textures (white, tinted by background_color) ──
_ASSETS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets')
BTN_BG      = os.path.join(_ASSETS, 'btn_round.png')
BTN_BG_DOWN = os.path.join(_ASSETS, 'btn_round_down.png')


def _lum(rgb):
    def f(c):
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = rgb[:3]
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def readable(hex_color):
    """Return a version of `hex_color` that is legible as TEXT on the
    current theme's card. Neon LED colours (yellow, mint...) vanish on a
    white card, so in light mode they are darkened until contrast >= 4.5."""
    if is_dark_theme():
        return hex_color
    r, g, b, _a = hex2rgba(hex_color)
    for _ in range(30):
        if 1.05 / (_lum((r, g, b)) + 0.05) >= 4.5:
            break
        r, g, b = r * 0.9, g * 0.9, b * 0.9
    return '#%02X%02X%02X' % (int(r * 255), int(g * 255), int(b * 255))


def mode_icon_text():
    """Glyph for the quick Dark/Light toggle (shows the mode you'll get)."""
    return '\u2600' if is_dark_theme() else '\u263E'
