"""
"""
import lvgl as lv
import ili9XXX
from ili9XXX import st7789
import fs_driver
import hashlib
import machine
import os
import time

from embit.bip39 import mnemonic_from_bytes


# FS driver init
fs_drv = lv.fs_drv_t()
fs_driver.fs_register(fs_drv, 'S')
opensans_semibold_20 = lv.font_load("S:/opensans_semibold_20.bin")
opensans_regular_17 = lv.font_load("S:/opensans_regular_17.bin")


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

scr.set_style_bg_color(lv.color_hex(0xffffff), 0)
scr.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)

### Top Nav ###
top_nav = lv.obj(scr)
top_nav.set_size(240, 48)
top_nav.align(lv.ALIGN.TOP_LEFT, 0, 0)

style = lv.style_t()
style.init()
style.set_pad_all(0)
style.set_border_width(0)
style.set_radius(0)
style.set_bg_color(lv.color_hex(0xffcc00))
top_nav.add_style(style, 0)

top_nav_label = lv.label(top_nav)
top_nav_label.set_text("Coin Flip #1 of 50")
top_nav_label.center()
top_nav_label_style = lv.style_t()
top_nav_label_style.set_text_font(opensans_semibold_20)
top_nav_label_style.set_text_color(lv.color_hex(0x000000))
top_nav_label.add_style(top_nav_label_style, 0)


flip_results = lv.label(scr)
flip_results.set_width(120)
flip_results.align_to(top_nav, lv.ALIGN.OUT_BOTTOM_MID, 0, 10)
flip_results.set_style_text_font(opensans_semibold_20, 0)
flip_results.set_style_text_color(lv.color_hex(0x000000), 0)
flip_results.set_text("")

instructions = lv.label(scr)
instructions.set_style_text_font(opensans_regular_17, 0)
instructions.set_text("LEFT to delete")
instructions.align(lv.ALIGN.BOTTOM_MID, 0, -5)

instructions2 = lv.label(scr)
instructions2.set_style_text_font(opensans_regular_17, 0)
instructions2.set_text("UP for heads; DOWN for tails")
instructions2.align_to(instructions, lv.ALIGN.OUT_TOP_MID, 0, 0)

flips = ""

while True:
    changed = False
    if joy_up.value() == 0:
        flips += "1"
        changed = True

    elif joy_down.value() == 0:
        flips += "0"
        changed = True
    
    elif joy_left.value() == 0:
        # Delete the last value
        flips = flips[:-1]
        changed = True

    if changed:
        top_nav_label.set_text(f"Coin Flip #{len(flips)+1} of 50")
        flip_results.set_text(flips)
        if len(flips) == 50:
            break

        time.sleep(0.2)
    

# Set up a second screen obj
mnemonic_scr = lv.obj()

# Generate 12-word mnemonic (16 bytes of input)
seed_bytes = hashlib.sha256(flips).digest()[:16]
mnemonic = mnemonic_from_bytes(seed_bytes)
print(flips)
print(mnemonic)

mnemonic_left = lv.label(mnemonic_scr)
mnemonic_left.set_style_text_font(opensans_semibold_20, 0)
mnemonic_left.align(lv.ALIGN.LEFT_MID, 5, 0)
mnemonic_left.set_style_text_color(lv.color_hex(0x000000), 0)
text = ""
for index in range(0, 6):
    text += f"{index+1}: {mnemonic.split()[index]}\n"
mnemonic_left.set_text(text)

mnemonic_right = lv.label(mnemonic_scr)
mnemonic_right.set_style_text_font(opensans_semibold_20, 0)
mnemonic_right.align(lv.ALIGN.RIGHT_MID, -5, 0)
mnemonic_right.set_style_text_color(lv.color_hex(0x000000), 0)
text = ""
for index in range(6, 12):
    text += f"{index+1}: {mnemonic.split()[index]}\n"
mnemonic_right.set_text(text)

# Make the second screen the active screen now
lv.scr_load(mnemonic_scr)
