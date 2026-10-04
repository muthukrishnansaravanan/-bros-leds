"""Menu Items Manager Screen"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.utils import get_color_from_hex
from utils.app_state import state
from utils.strings import s
from utils.theme import BTN_BG, BTN_BG_DOWN, readable, mode_icon_text
from utils.theme import (t, hex2rgba, PAD, CARD_PAD, BTN_H, MD, LG, SM, XS,
                          XL, RADIUS, FONT_TEXT, FONT_ICON)
from utils.widgets import Card, HeaderBar, btn, lbl, section
from utils.icons import icon

CATEGORIES = ['Starters', 'Main', 'Dessert', 'Beverages', 'Specials', 'Others']
ITEM_COLORS = ['#FFD700','#00FF88','#FF6B6B','#4FC3F7','#FF69B4',
               '#FFA500','#00E676','#FF5252','#CE93D8','#80DEEA']


def rgba(h):
    return get_color_from_hex(h)


class MenuScreen(Screen):

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
        root.add_widget(HeaderBar('Menu Items', self, icon_name='menu_items'))

        # Add button bar
        top_bar = BoxLayout(size_hint_y=None, height=52,
                            padding=[PAD, 6], spacing=8)
        with top_bar.canvas.before:
            Color(*hex2rgba(t('header')))
            tb_r = Rectangle(pos=top_bar.pos, size=top_bar.size)
        top_bar.bind(pos=lambda w, v: setattr(tb_r, 'pos', v),
                     size=lambda w, v: setattr(tb_r, 'size', v))

        self.count_lbl = Label(
            text=f'{len(state.menu_items)} items',
            font_name=FONT_TEXT, font_size=SM, color=hex2rgba(t('sub')),
            halign='left', valign='middle',
        )
        self.count_lbl.bind(size=self.count_lbl.setter('text_size'))
        top_bar.add_widget(self.count_lbl)

        add_b = btn(f'{icon("plus")} Add Item', bg=t('btn_ok'), fg='#000000',
                    height=40, fs=SM, bold=True)
        add_b.font_name = FONT_ICON
        add_b.size_hint_x = 0.4
        add_b.bind(on_press=lambda x: self._open_form())
        top_bar.add_widget(add_b)
        root.add_widget(top_bar)

        # List
        self.sv = ScrollView()
        self.list_box = BoxLayout(orientation='vertical',
                                   padding=[PAD, PAD],
                                   spacing=8, size_hint_y=None)
        self.list_box.bind(minimum_height=self.list_box.setter('height'))
        self._rebuild()
        self.sv.add_widget(self.list_box)
        root.add_widget(self.sv)

        self.add_widget(root)

    def _rebuild(self):
        self.list_box.clear_widgets()
        cats = {}
        for item in state.menu_items:
            cats.setdefault(item['category'], []).append(item)

        for cat, items in cats.items():
            self.list_box.add_widget(section(f'{cat}'))
            for item in items:
                self.list_box.add_widget(self._item_row(item))

        self.count_lbl.text = f'{len(state.menu_items)} items'

    def _item_row(self, item):
        row = Card(size_hint_y=None, height=58,
                   orientation='horizontal',
                   padding=[CARD_PAD, 0], spacing=8)

        # Color dot
        dot = Label(
            text=icon('dot'), font_name=FONT_ICON, font_size=LG,
            size_hint=(None, None), size=(24, 40),
            color=rgba(readable(item.get('color', '#FFD700'))),
        )
        row.add_widget(dot)

        # Info
        info = BoxLayout(orientation='vertical')
        n = Label(
            text=item["name"],
            font_name=FONT_TEXT, bold=True, font_size=MD,
            color=hex2rgba(t('text')),
            halign='left', valign='middle',
        )
        n.bind(size=n.setter('text_size'))
        p = Label(
            text=f'{item["price"]}  ·  {item["category"]}',
            font_name=FONT_TEXT, font_size=XS, color=hex2rgba(t('sub')),
            halign='left', valign='middle',
        )
        p.bind(size=p.setter('text_size'))
        info.add_widget(n)
        info.add_widget(p)
        row.add_widget(info)

        # Buttons
        btn_box = BoxLayout(size_hint=(None, None),
                             size=(130, 40), spacing=4)

        send_b = Button(
            text=icon('send'), font_name=FONT_ICON, font_size=MD,
            color=rgba('#000000'),
            background_normal=BTN_BG, background_down=BTN_BG_DOWN, background_color=rgba('#00E676'),
        )
        send_b.bind(on_press=lambda x, it=item: self._send_item(it))

        edit_b = Button(
            text=icon('edit'), font_name=FONT_ICON, font_size=MD,
            color=rgba('#FFFFFF'),
            background_normal=BTN_BG, background_down=BTN_BG_DOWN, background_color=rgba('#1565C0'),
        )
        edit_b.bind(on_press=lambda x, it=item: self._open_form(it))

        del_b = Button(
            text=icon('delete'), font_name=FONT_ICON, font_size=MD,
            color=rgba('#FFFFFF'),
            background_normal=BTN_BG, background_down=BTN_BG_DOWN, background_color=rgba('#C62828'),
        )
        del_b.bind(on_press=lambda x, it=item: self._delete(it))

        btn_box.add_widget(send_b)
        btn_box.add_widget(edit_b)
        btn_box.add_widget(del_b)
        row.add_widget(btn_box)

        return row

    def _send_item(self, item):
        from commands.led_commands import get_board
        state.text_content = f'{item["name"]}  {item["price"]}'
        state.text_color   = item.get('color', '#FFD700')
        board = get_board(state.device_ip)
        if board.connect():
            board.sync_time()
            board.send_content(state)
            board.disconnect()

    def _delete(self, item):
        if item in state.menu_items:
            state.menu_items.remove(item)
            state.save()
            self._rebuild()

    def _open_form(self, item=None):
        popup = _ItemForm(item, on_save=self._on_save)
        popup.open()

    def _on_save(self, item, original=None):
        if original and original in state.menu_items:
            idx = state.menu_items.index(original)
            state.menu_items[idx] = item
        else:
            state.menu_items.append(item)
        state.save()
        self._rebuild()

    def on_enter(self):
        self._rebuild()


class _ItemForm(Popup):

    def __init__(self, item=None, on_save=None, **kw):
        self._original = item
        self._on_save  = on_save
        kw['title']      = 'Edit Item' if item else 'Add Menu Item'
        kw['size_hint']  = (0.92, 0.72)
        kw['background_color'] = get_color_from_hex(t('card'))
        super().__init__(**kw)

        root = BoxLayout(orientation='vertical', padding=14, spacing=10)

        # Name
        root.add_widget(Label(text='Item Name', font_name=FONT_TEXT, font_size=SM,
                               color=get_color_from_hex(t('sub')),
                               size_hint_y=None, height=22,
                               halign='left', valign='middle'))
        self.name_in = TextInput(
            text=item['name'] if item else '',
            hint_text='e.g. Chicken Biryani',
            font_name=FONT_TEXT, font_size=MD, multiline=False,
            size_hint_y=None, height=44,
            background_color=get_color_from_hex(t('input_bg')),
            foreground_color=get_color_from_hex(t('text')),
        )
        root.add_widget(self.name_in)

        # Price
        root.add_widget(Label(text='Price', font_name=FONT_TEXT, font_size=SM,
                               color=get_color_from_hex(t('sub')),
                               size_hint_y=None, height=22,
                               halign='left', valign='middle'))
        self.price_in = TextInput(
            text=item['price'] if item else '₹',
            font_name=FONT_TEXT, font_size=MD, multiline=False,
            size_hint_y=None, height=44,
            background_color=get_color_from_hex(t('input_bg')),
            foreground_color=get_color_from_hex(t('text')),
        )
        root.add_widget(self.price_in)

        # Category
        root.add_widget(Label(text='Category', font_name=FONT_TEXT, font_size=SM,
                               color=get_color_from_hex(t('sub')),
                               size_hint_y=None, height=22,
                               halign='left', valign='middle'))
        self.cat_spin = Spinner(
            text=item['category'] if item else 'Main',
            values=CATEGORIES,
            size_hint_y=None, height=44,
            font_name=FONT_TEXT, font_size=MD,
            background_color=get_color_from_hex('#1565C0'),
            color=get_color_from_hex('#FFFFFF'),
        )
        root.add_widget(self.cat_spin)

        # Color picker
        root.add_widget(Label(text='Color', font_name=FONT_TEXT, font_size=SM,
                               color=get_color_from_hex(t('sub')),
                               size_hint_y=None, height=22,
                               halign='left', valign='middle'))
        from kivy.uix.gridlayout import GridLayout
        cg = GridLayout(cols=5, size_hint_y=None, height=50, spacing=4)
        self._sel_color = item.get('color', '#FFD700') if item else '#FFD700'
        self._color_btns = {}
        for c in ITEM_COLORS:
            cb = Button(
                background_normal=BTN_BG, background_down=BTN_BG_DOWN, background_color=get_color_from_hex(c),
                size_hint_y=None, height=42,
            )
            cb.bind(on_press=lambda x, cc=c: self._pick_color(cc))
            self._color_btns[c] = cb
            cg.add_widget(cb)
        root.add_widget(cg)

        # Buttons
        btn_row = BoxLayout(size_hint_y=None, height=48, spacing=10)
        cancel_b = Button(
            text='Cancel', font_name=FONT_TEXT, bold=True, font_size=MD,
            color=get_color_from_hex('#FFFFFF'),
            background_normal=BTN_BG, background_down=BTN_BG_DOWN, background_color=get_color_from_hex('#37474F'),
        )
        cancel_b.bind(on_press=lambda x: self.dismiss())
        save_b = Button(
            text='Save', font_name=FONT_TEXT, bold=True, font_size=MD,
            color=get_color_from_hex('#000000'),
            background_normal=BTN_BG, background_down=BTN_BG_DOWN, background_color=get_color_from_hex(t('btn_ok')),
        )
        save_b.bind(on_press=self._save)
        btn_row.add_widget(cancel_b)
        btn_row.add_widget(save_b)
        root.add_widget(btn_row)

        self.content = root

    def _pick_color(self, c):
        self._sel_color = c

    def _save(self, _):
        name  = self.name_in.text.strip()
        price = self.price_in.text.strip()
        if not name or not price:
            return
        new_item = {
            'name': name, 'price': price,
            'category': self.cat_spin.text,
            'color': self._sel_color,
        }
        if self._on_save:
            self._on_save(new_item, self._original)
        self.dismiss()
