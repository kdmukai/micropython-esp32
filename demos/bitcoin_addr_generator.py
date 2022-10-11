"""
"""
import lvgl as lv
import ili9XXX
from ili9XXX import st7789
import fs_driver
import machine
import os
import time

from embit import bip39, bip32, script


lv.init()

"""
    Pinouts for different boards:

    ESP32-S3-DevKitC-1:
        FSPID (11) = MOSI
        mosi=11, clk=12, cs=10, dc=4, rst=5,

    Unexpected Maker FeatherS3:
        mosi=12, clk=6, cs=17, dc=14, rst=18,

    Saola-1R:
        mosi=11, clk=12, cs=10, dc=1, rst=2,
"""
disp = st7789(
    mosi=11, clk=12, cs=10, dc=1, rst=2,
    width=240, height=240, rot=ili9XXX.LANDSCAPE
)

scr = lv.scr_act()
scr.clean()

scr.set_style_bg_color(lv.color_hex(0xFFFFFF), 0)
scr.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)

NATIVE_SEGWIT = "m/84'/0'/0'"
NESTED_SEGWIT = "m/49'/0'/0'"
TAPROOT = "m/86'/0'/0'"


def xpub_from_mnemonic(mnemonic, derivation_path):
    seed = bip39.mnemonic_to_seed(mnemonic)
    root = bip32.HDKey.from_seed(seed)
    xprv = root.derive(derivation_path)
    return xprv.to_public()


def generate_address(xpub, derivation_path, index: int):
    # generate first receive addr
    pubkey = xpub.derive([0,index]).key

    if derivation_path == NATIVE_SEGWIT:
        return script.p2wpkh(pubkey).address()

    elif derivation_path == NESTED_SEGWIT:
        return script.p2sh(script.p2wpkh(pubkey)).address()
    
    elif derivation_path == TAPROOT:
        return script.p2tr(pubkey).address()


# Generate a random 12-word mnemonic
seed_bytes = os.urandom(16)
mnemonic = bip39.mnemonic_from_bytes(seed_bytes)
print(mnemonic)

xpubs = [
    {
        "name": "Segwit",
        "xpub": xpub_from_mnemonic(mnemonic, NATIVE_SEGWIT),
        "derivation_path": NATIVE_SEGWIT,
    },
    {
        "name": "Nested segwit",
        "xpub": xpub_from_mnemonic(mnemonic, NESTED_SEGWIT),
        "derivation_path": NESTED_SEGWIT,
    },
    {
        "name": "Taproot",
        "xpub": xpub_from_mnemonic(mnemonic, TAPROOT),
        "derivation_path": TAPROOT,
    },
]

cur_xpub_index = 0
cur_xpub = xpubs[cur_xpub_index]
cur_addr_index = 0

qr = lv.qrcode(scr, 180, lv.color_hex(0x000000), lv.color_hex(0xFFFFFF))

# FS driver init
fs_drv = lv.fs_drv_t()
fs_driver.fs_register(fs_drv, 'S')
opensans_semibold_20 = lv.font_load("S:/opensans_semibold_20.bin")
opensans_regular_17 = lv.font_load("S:/opensans_regular_17.bin")

img_label = lv.label(scr)
img_label.center()
img_label.set_style_text_font(opensans_semibold_20, 0)
img_label.align(lv.ALIGN.BOTTOM_LEFT, 5, -5)
img_label.set_style_text_color(lv.color_hex(0x000000), 0)

def render_addr_qrcode():
    addr = generate_address(xpub=cur_xpub["xpub"], derivation_path=cur_xpub["derivation_path"], index=cur_addr_index)
    print(addr)
    qr.update(addr,len(addr))
    qr.align(lv.ALIGN.TOP_MID, 0, 5)

    img_label.set_text(f"""{cur_xpub["name"]}: #{cur_addr_index}\n{addr[:7]}...{addr[-7:]}""")
    return addr

render_addr_qrcode()

key1 = machine.Pin(3, machine.Pin.IN, machine.Pin.PULL_UP)
key2 = machine.Pin(34, machine.Pin.IN, machine.Pin.PULL_UP)
key3 = machine.Pin(33, machine.Pin.IN, machine.Pin.PULL_UP)

joy_up = machine.Pin(13, machine.Pin.IN, machine.Pin.PULL_UP)
joy_down = machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_UP)
joy_left = machine.Pin(15, machine.Pin.IN, machine.Pin.PULL_UP)
joy_right = machine.Pin(16, machine.Pin.IN, machine.Pin.PULL_UP)
joy_press = machine.Pin(17, machine.Pin.IN, machine.Pin.PULL_UP)

buttons = [
    (key1, "KEY1"),
    (key2, "KEY2"),
    (key3, "KEY3"),
    (joy_up, "UP"),
    (joy_down, "DOWN"),
    (joy_left, "LEFT"),
    (joy_right, "RIGHT"),
    (joy_press, "PRESS"),
]

while True:
    if joy_right.value() == 0:
        # Advance the current addr index
        cur_addr_index += 1
        addr = render_addr_qrcode()

    elif joy_left.value() == 0:
        # Backup the current addr index
        cur_addr_index -= 1
        if cur_addr_index < 0:
            cur_addr_index = 0
        addr = render_addr_qrcode()
    
    elif joy_up.value() == 0:
        cur_xpub_index -= 1
        if cur_xpub_index < 0:
            cur_xpub_index = len(xpubs) - 1
        cur_xpub = xpubs[cur_xpub_index]
        addr = render_addr_qrcode()

    elif joy_down.value() == 0:
        cur_xpub_index += 1
        if cur_xpub_index == len(xpubs):
            cur_xpub_index = 0
        cur_xpub = xpubs[cur_xpub_index]
        addr = render_addr_qrcode()

    time.sleep(0.1)

