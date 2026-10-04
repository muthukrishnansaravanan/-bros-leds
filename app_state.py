"""Global App State — All screens share this"""
import json, os

DATA_FILE = 'data/menu_data.json'

EXPORT_FIELDS = [
    'menu_items', 'theme', 'language', 'device_ip', 'brightness',
    'text_content', 'text_color', 'text_size', 'bg_color',
    'scroll_speed', 'scroll_direction', 'scroll_effect',
    'clock_enabled', 'clock_format', 'clock_color',
    'font_name', 'font_bold', 'font_italic', 'font_underline',
    'text_align', 'anim_effect', 'hold_seconds', 'immediate_clear',
    'border_enabled', 'border_color', 'canvas_rotation',
]


class AppState:
    # Auth
    logged_in   = False
    username    = ''
    users       = {'admin': 'bros123'}   # username: password

    # Device
    device_ip    = '192.168.1.100'
    device_name  = 'Not Connected'
    is_connected = False

    # Display content
    text_content     = 'Welcome to BRO\'S Hotel!'
    text_color       = '#FFD700'
    text_size        = 28
    bg_color         = '#000000'
    scroll_speed     = 5
    scroll_direction = 'left'
    scroll_effect    = 'normal'

    # Clock
    clock_enabled = True
    clock_format  = '12h'
    clock_color   = '#FFFFFF'

    # Image
    image_path    = None
    image_enabled = False

    # Brightness (0–100)
    brightness = 80

    # Theme: 'dark' | 'blue' | 'purple' | 'green' | 'light'
    theme = 'dark'

    # Language: 'en' | 'ta'
    language = 'en'

    # ── Program Editor (LEDArt-style single-program settings) ──────
    font_name        = 'Arial'
    font_bold        = False
    font_italic      = False
    font_underline   = False
    text_align       = 'left'          # left | center | right
    anim_effect      = 'Display static'
    hold_seconds     = 3
    immediate_clear  = False
    border_enabled   = False
    border_color     = '#FF0000'
    canvas_rotation  = 'Normal'        # Normal | 90 | 180 | 270

    # Menu items
    menu_items = [
        {'name': 'Chicken Biryani', 'price': '₹180', 'category': 'Main',     'color': '#FFD700'},
        {'name': 'Veg Meals',       'price': '₹100', 'category': 'Main',     'color': '#00FF88'},
        {'name': 'Mutton Curry',    'price': '₹250', 'category': 'Main',     'color': '#FF6B6B'},
        {'name': 'Spring Rolls',    'price': '₹80',  'category': 'Starters', 'color': '#4FC3F7'},
        {'name': 'Gulab Jamun',     'price': '₹60',  'category': 'Dessert',  'color': '#FF69B4'},
        {'name': 'Filter Coffee',   'price': '₹20',  'category': 'Beverages','color': '#FFA500'},
    ]

    def save(self):
        os.makedirs('data', exist_ok=True)
        with open(DATA_FILE, 'w') as f:
            json.dump(self._to_dict(), f, indent=2)

    def load(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE) as f:
                    d = json.load(f)
                self._from_dict(d)
            except Exception:
                pass

    def _to_dict(self):
        d = {field: getattr(self, field) for field in EXPORT_FIELDS}
        d['users'] = self.users
        return d

    def _from_dict(self, d):
        for field in EXPORT_FIELDS:
            if field in d:
                setattr(self, field, d[field])
        if 'users' in d:
            self.users = d['users']

    # ── Import / Export to a plain .txt file ────────────────────────
    def export_to_txt(self, path, include_users=False):
        """Write all app settings + menu items as readable JSON text."""
        data = self._to_dict()
        if not include_users:
            data.pop('users', None)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True

    def import_from_txt(self, path):
        """Read a previously exported .txt file and apply it. Raises
        ValueError with a human-readable message on bad input."""
        with open(path, 'r', encoding='utf-8') as f:
            raw = f.read()
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            raise ValueError(f'Not a valid export file ({e})')
        if not isinstance(data, dict):
            raise ValueError('File does not contain app settings')
        self._from_dict(data)
        self.save()
        return True


state = AppState()
