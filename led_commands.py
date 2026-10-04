"""
WF2 LED Board Commands
TCP Port: 9527
Opcodes: kContentStartAsk=512, kContentDataAsk=514, kContentEndAsk=516
"""

import socket, struct, json, time
from datetime import datetime

PORT       = 9527
TIMEOUT    = 5
CHUNK      = 1024

# Confirmed opcodes from APK decompile
OP_VERSION      = 0x100   # 256
OP_TIME_SYNC    = 0x101   # 257
OP_BRIGHTNESS   = 0x102   # 258
OP_POWER        = 0x103   # 259
OP_CONTENT_START= 0x200   # 512
OP_CONTENT_DATA = 0x202   # 514
OP_CONTENT_END  = 0x204   # 516


def discover_boards(timeout=3):
    boards = []
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(timeout)
        sock.sendto(b'LEDART_DISCOVER', ('<broadcast>', PORT))
        while True:
            try:
                data, addr = sock.recvfrom(1024)
                boards.append({
                    'ip': addr[0],
                    'name': data.decode('utf-8', errors='ignore') or f'WF2-{addr[0]}'
                })
            except socket.timeout:
                break
    except Exception as e:
        print(f'[Discover] {e}')
    finally:
        try: sock.close()
        except: pass
    return boards


class LedBoard:
    def __init__(self, ip):
        self.ip   = ip
        self.sock = None

    def connect(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(TIMEOUT)
            self.sock.connect((self.ip, PORT))
            return True
        except Exception as e:
            print(f'[Connect] {e}')
            return False

    def disconnect(self):
        if self.sock:
            try: self.sock.close()
            except: pass
            self.sock = None

    def _send(self, opcode, payload=b''):
        """Send: 4-byte magic + 2-byte opcode + 4-byte length + payload"""
        header = b'LART' + struct.pack('>HI', opcode, len(payload))
        try:
            self.sock.sendall(header + payload)
            return True
        except Exception as e:
            print(f'[Send] {e}')
            return False

    def _recv(self):
        try: return self.sock.recv(1024)
        except: return b''

    def get_version(self):
        self._send(OP_VERSION)
        r = self._recv()
        try:    return json.loads(r[10:].decode())
        except: return {}

    def sync_time(self):
        n = datetime.now()
        p = struct.pack('>HBBBBB',
            n.year, n.month, n.day,
            n.hour, n.minute, n.second)
        self._send(OP_TIME_SYNC, p)

    def set_brightness(self, level: int):
        """level: 0-100"""
        self._send(OP_BRIGHTNESS, struct.pack('>B', max(0, min(100, level))))

    def power(self, on: bool):
        self._send(OP_POWER, struct.pack('>B', 1 if on else 0))

    def send_content(self, st):
        """Build XML and stream to board in chunks"""
        xml   = _build_xml(st)
        data  = xml.encode('utf-8')
        total = len(data)

        # Start
        self._send(OP_CONTENT_START, struct.pack('>I', total))
        time.sleep(0.1)

        # Chunks
        for i in range(0, total, CHUNK):
            chunk = data[i:i+CHUNK]
            self._send(OP_CONTENT_DATA, chunk)
            time.sleep(0.05)

        # End
        self._send(OP_CONTENT_END)
        return True


def _build_xml(st):
    """
    XML content builder.
    NOTE: Structure is best-effort from APK decompile (toXml() method).
    Confirm/update after first Wireshark capture with real board.
    """
    nodes = []

    if st.text_content:
        c = st.text_color.replace('#', '')
        b = st.bg_color.replace('#', '')
        nodes.append(
            f'<Node type="Text">'
            f'<Text value="{st.text_content}" color="{c}" '
            f'size="{st.text_size}" bg="{b}"/>'
            f'<Effect type="{st.scroll_effect}" '
            f'dir="{st.scroll_direction}" speed="{st.scroll_speed}"/>'
            f'</Node>'
        )

    if st.clock_enabled:
        cc = st.clock_color.replace('#', '')
        nodes.append(
            f'<Node type="Clock">'
            f'<Clock fmt="{st.clock_format}" color="{cc}"/>'
            f'</Node>'
        )

    if st.image_enabled and st.image_path:
        nodes.append(
            f'<Node type="Image">'
            f'<Image src="{st.image_path}"/>'
            f'</Node>'
        )

    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<Program version="1">'
        '<Screen w="64" h="32">'
        + ''.join(nodes) +
        '</Screen></Program>'
    )


# ── Mock Board ─────────────────────────────────────────

class MockLedBoard:
    def __init__(self, ip='192.168.1.100'):
        self.ip = ip

    def connect(self):
        print(f'[MOCK] Connected → {self.ip}')
        return True

    def disconnect(self):
        print('[MOCK] Disconnected')

    def get_version(self):
        return {'fw': 'WF2-v3.17', 'model': 'P10-RGB'}

    def sync_time(self):
        print(f'[MOCK] TimeSync → {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}')

    def set_brightness(self, level):
        print(f'[MOCK] Brightness → {level}%')

    def power(self, on):
        print(f'[MOCK] Power → {"ON" if on else "OFF"}')

    def send_content(self, st):
        print('=' * 50)
        print(f'[MOCK] MSG      : {st.text_content}')
        print(f'[MOCK] COLOR    : {st.text_color} on {st.bg_color}')
        print(f'[MOCK] SCROLL   : {st.scroll_direction} | speed={st.scroll_speed}')
        print(f'[MOCK] EFFECT   : {st.scroll_effect}')
        print(f'[MOCK] CLOCK    : {"ON" if st.clock_enabled else "OFF"} ({st.clock_format})')
        print(f'[MOCK] BRIGHTNESS:{st.brightness}%')
        print('=' * 50)
        return True


USE_MOCK = True   # ← Board வந்ததும் False பண்ணு


def get_board(ip=None):
    if USE_MOCK:
        return MockLedBoard(ip or '192.168.1.100')
    return LedBoard(ip or '192.168.1.100')
