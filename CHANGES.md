# BRO'S LED Controller — Fix Log

All 8 requested fixes, what was actually wrong, and what changed.

## 1. Password field — SHOW/HIDE option
Login & Signup password fields now have a SHOW/HIDE button next to them
(`utils/widgets.py` → `PasswordField`). Tap it to reveal what you typed
before submitting.

## 2. All buttons showing the same icon
**Root cause:** Kivy's default UI font ("Roboto") contains almost none of
the emoji glyphs the app used (📋 📺 🎨 📡 🗑 ❓ 🌐 etc). On a real phone
every icon-only button rendered as the same empty "missing glyph" box —
it wasn't a styling bug, it was a missing-character bug.
**Fix:** switched icons to Kivy's other bundled font (`DejaVuSans`, no
extra asset needed) and a curated "safe icon set" (`utils/icons.py`)
where every character was verified against that font's actual glyph
table. Nav buttons now also show icon + readable word together.

## 3. Date & time not clearly visible
Date & Time screen rebuilt: large 36pt clock, bold date, on a
high-contrast card instead of plain background text. Home screen also
shows a bigger, bolder live clock next to the date.

## 4. Fonts too bold / "smoothy"
Removed the `[b]...[/b]` markup that was forcing bold almost everywhere.
Body text is now regular weight; bold is reserved for headings and
primary buttons only.

## 5. Missing back button on screens
**Root cause (real bug, not just missing UI):** `HeaderBar` was built
inside each screen's `__init__`, at which point `self.manager` is still
`None` (a screen only gets a manager once it's added to the
`ScreenManager`). The back button's visibility check silently failed
every time, so it never rendered on *any* screen, even in the original
code.
**Fix:** `HeaderBar` now takes the screen itself and resolves
`screen.manager` lazily when the button is actually pressed, not at
construction time. Verified on all 10 non-home screens.

## 6. Light / Dark theme for user-friendliness
Added a 5th theme, **Light**, alongside Dark/Blue/Purple/Green
(`utils/theme.py`). Switch it in Settings → App Theme.

## 7. LEDArt-style Program Editor screen
Added a new **Program Editor** screen (from the Home nav grid) matching
the reference screenshot: text box, font family/size/color,
Bold/Italic/Underline, text alignment, animation effect, speed, hold
time, immediate clear, border, and canvas rotation.

## 8. Import / Export as .txt
Settings → Backup now has Export and Import buttons. Export writes all
your app settings and menu items to a `.txt` file (JSON-formatted,
human-readable) via a save dialog; Import reads one back via an open
dialog filtered to `.txt` files.

---
### Testing performed
All 13 screens were built and laid out headlessly with real Kivy +
Xvfb (not just syntax-checked). The back-button fix, password
show/hide, theme switching, and import/export round-trip were each
verified by actually simulating button presses and checking resulting
state, not just reading the code.

---
# Update 2 — Themes, widgets, intro video

## A. Dark / Light theme on EVERY page (live, no restart)
* Root cause: screens read the theme only once when they were built, so
  changing it did nothing until restart, and Login was hard-coded dark.
* `main.py → apply_theme()` now re-skins all pages instantly.
* Saved theme is loaded BEFORE screens are built (was loaded too late).
* Quick toggle button (sun/moon) in the header of every page, the Home
  header and the Login page. Settings → App Theme still has all 5 themes.
* Light theme contrast fixed: neon LED colours are auto-darkened when
  used as text on white (`readable()`), status green is theme-aware.

## B. Widget quality
* All buttons are now rounded with a pressed state (`assets/btn_round*.png`).
* Cards have a soft outline (visible on light theme), headers a divider line.

## C. 10-second intro video (phone "boot" style)
* `assets/intro.mp4` plays full-screen once when the app opens, with
  sound, then fades into Login (`screens/splash_screen.py`).
* Ends at video end (max 10.6 s). If the video cannot play on a device,
  it falls back to the animated logo so the app never hangs.
* Needs `ffpyplayer` (added to requirements.txt and buildozer.spec; `mp4`
  added to `source.include_exts`).
