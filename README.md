# BRO'S LED Controller
### Hotel Menu Display App — Python + Kivy
**BRO'S Engineering Solution Pvt.Ltd.**

---

## Features
| Screen | What it does |
|--------|-------------|
| Splash | Company logo animation on startup |
| Login / Sign Up | Secure access with username & password |
| Home Dashboard | Live clock, quick send, all features |
| Menu Items | Add/Edit/Delete items with Name, Price, Category, Color |
| Display Message | Type custom text, font size, quick messages |
| Colors | Text color + background color picker |
| Scroll Settings | Direction, speed, effect (Normal/Blink/Wave…) |
| Brightness | 0–100% slider + quick presets |
| Date & Time | Live clock, 12h/24h, sync to board |
| Connect Board | Auto scan WiFi or manual IP entry |
| Tutorial | Step-by-step user guide |
| Settings | Theme (Dark/Blue/Purple/Green), Language (EN/Tamil) |

---

## Setup — VS Code

### Step 1: Install Python 3.11
```bash
python --version   # should be 3.10 or 3.11
```

### Step 2: Create virtual environment
```bash
python -m venv venv

# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate
```

### Step 3: Install dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run the app
```bash
python main.py
```

---

## Connect to Real WF2 Board

1. Open `commands/led_commands.py`
2. Change line: `USE_MOCK = True` → `USE_MOCK = False`
3. In app → Go to **Connect Board** → Enter board IP → Connect
4. Tap ⚡ **SEND TO BOARD** from Home screen

> **Note:** XML content format is best-effort from APK decompile.
> If board doesn't display correctly, do one Wireshark capture
> and share — format will be corrected in 5 minutes.

---

## Build APK (Android)

Requires Linux or WSL2 + buildozer:

```bash
pip install buildozer
buildozer init
buildozer android debug
```

APK will be in `bin/` folder.

---

## Default Login
- **Username:** admin  
- **Password:** bros123

You can create new accounts from the Sign Up tab.

---

## File Structure
```
bros_led_app/
├── main.py                  ← App entry point
├── requirements.txt
├── README.md
├── assets/
│   └── logo.png             ← BRO'S company logo
├── commands/
│   └── led_commands.py      ← WF2 TCP protocol (port 9527)
├── screens/
│   ├── splash_screen.py     ← Logo splash
│   ├── login_screen.py      ← Login + Signup
│   ├── home_screen.py       ← Dashboard
│   ├── menu_screen.py       ← Menu manager
│   └── other_screens.py     ← Display/Color/Scroll/Brightness/etc.
└── utils/
    ├── app_state.py         ← Global state + data save/load
    ├── theme.py             ← 4 color themes
    ├── strings.py           ← EN / Tamil translations
    └── widgets.py           ← Reusable UI components
```

---

*Three Friends. One Vision. Endless Innovation.*
