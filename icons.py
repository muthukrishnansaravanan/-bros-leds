"""
Safe Icon Set
=============
Kivy's default UI font ("Roboto", bundled inside the kivy package) does
NOT contain glyphs for pictographic emoji (📋 📺 🎨 📡 🗑 ❓ 🌐 ...).
On a real phone this makes every icon-only button render as the exact
same empty "missing glyph" box — which is why every button looked
identical.

Every character below has been verified against Kivy's bundled
DejaVuSans.ttf (which ships with Kivy on every platform, including
Android via python-for-android — no extra font file needed). Labels
and Buttons that show one of these icons must set
font_name=utils.theme.FONT_ICON.
"""

ICON = {
    'home':        '⌂',
    'menu_items':  '☰',
    'display':     '▭',
    'brightness':  '☀',
    'bright_lo':   '☾',
    'bright_hi':   '☀',
    'clock':       '◷',
    'palette':     '●',
    'scroll':      '⇄',
    'program':     '▤',
    'device':      '◉',
    'help':        '?',
    'settings':    '⚙',
    'back':        '◀',
    'forward':     '▶',
    'edit':        '✎',
    'delete':      '✗',
    'send':        '➤',
    'plus':        '+',
    'power':       '◐',   # ⏻ has no glyph in the bundled font, this does
    'globe':       '◍',
    'eye_on':      '◉',
    'eye_off':     '⊘',
    'check':       '✓',
    'cross':       '✗',
    'up':          '▲',
    'down':        '▼',
    'left':        '◀',
    'right':       '▶',
    'dot':         '●',
    'dot_hollow':  '○',
    'star':        '★',
    'warn':        '⚠',
    'info':        'ℹ',
    'import':      '⬇',
    'export':      '⬆',
    'refresh':     '↻',
    'wifi':        '◉',
    'lock':        '◈',
}


def icon(name):
    """Return the safe glyph for `name`, or a bullet if unknown."""
    return ICON.get(name, '•')
